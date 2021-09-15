import itertools

import cv2
import numpy as np


def concat_min(images, boxes=[], by="horizontal", interpolation=cv2.INTER_CUBIC):
    assert images, "'images' is empty"

    if len(images) == 1:
        if len(boxes) == 1:
            return images[0], boxes[0]
        elif len(boxes) == 0:
            return images[0], []
        else:
            raise AssertionError(
                f"number of images (got {len(images)}) is not matched \
                with number of boxes (got {len(boxes)})"
            )

    # shape is (height, width)
    if by == "horizontal":
        min_dim, scaled_dim = 0, 1
        concat_func = cv2.hconcat
    elif by == "vertical":
        min_dim, scaled_dim = 1, 0
        concat_func = cv2.vconcat
    else:
        raise (ValueError("'by' must be one of 'horizaontal' or 'vertical'"))

    min_lens = [min([img.shape[min_dim] for img in images])] * len(images)
    scaled_lens = [
        round(img.shape[scaled_dim] * min_lens[0] / img.shape[min_dim]) for img in images
    ]
    sizes = [
        (lens[scaled_dim], lens[min_dim]) for lens in zip(min_lens, scaled_lens)
    ]  # width, height

    images_resized = [
        cv2.resize(img, size, interpolation=interpolation) for img, size in zip(images, sizes)
    ]
    if not boxes:
        return concat_func(images_resized), []

    assert len(images) == len(
        boxes
    ), f"number of images (got {len(images)}) is not matched with number of boxes (got {len(boxes)})"

    box_shifts = itertools.accumulate(
        [0] + [size[min_dim] for size in sizes[:-1]]
    )  # size in (width, height)
    boxes_resized = []
    for boxes_per_img, img, img_r, shift in zip(boxes, images, images_resized, box_shifts):
        # x, y, w, h
        boxes_per_img = np.array(boxes_per_img, dtype=float)
        if len(boxes_per_img) == 0:
            boxes_per_img = boxes_per_img.reshape((0, 4))

        boxes_per_img[:, scaled_dim::2] *= img_r.shape[min_dim] / img.shape[min_dim]
        boxes_per_img[:, min_dim::2] *= img_r.shape[scaled_dim] / img.shape[scaled_dim]
        boxes_per_img[:, min_dim] += shift
        boxes_resized.append(boxes_per_img)

    return concat_func(images_resized), np.concatenate(boxes_resized, axis=0)


def synthesize(nrow, ncol, images, boxes):
    mosaics_per_row, boxes_per_row = [], []
    for row in range(nrow):
        images_row = images[row * ncol : (row + 1) * ncol]
        boxes_row = boxes[row * ncol : (row + 1) * ncol]

        if len(images_row) == 0:
            break

        mosaic_row, boxes_row = concat_min(images_row, boxes_row, by="horizontal")
        mosaics_per_row.append(mosaic_row)
        boxes_per_row.append(boxes_row)

    mosaic, boxes = concat_min(mosaics_per_row, boxes_per_row, by="vertical")
    return mosaic, boxes


def worker_exec(args, img_dicts, id):
    # img_dicts = images[img_dicts_id]
    # each dict looks like:
    # {'license': 4,
    # 'file_name': '000000397133.jpg',
    # 'coco_url': 'http://images.cocodataset.org/val2017/000000397133.jpg',
    # 'height': 427,
    # 'width': 640,
    # 'date_captured': '2013-11-14 17:02:52',
    # 'flickr_url': 'http://farm7.staticflickr.com/6116/6255196340_da26cf2c9e_z.jpg',
    # 'id': 397133}
    imgs = [args.img_dir.joinpath(*img_dict["coco_url"].split("/")[-2:]) for img_dict in img_dicts]
    for img in imgs:
        if not img.is_file():
            raise FileNotFoundError(f"'{img}' does not exist. ")

    imgs = [cv2.imread(str(img)) for img in imgs]

    img_ids = [img_dict["id"] for img_dict in img_dicts]
    bboxes = [[ann["bbox"] for ann in img_dict["annotations"]] for img_dict in img_dicts]
    category_ids = list(
        itertools.chain(
            *[[ann["category_id"] for ann in img_dict["annotations"]] for img_dict in img_dicts]
        )
    )
    iscrowds = list(
        itertools.chain(
            *[[ann["iscrowd"] for ann in img_dict["annotations"]] for img_dict in img_dicts]
        )
    )

    mosaic, bboxes = synthesize(args.nrow, args.ncol, imgs, bboxes)
    img_path = args.output_dir.joinpath("images", f"{id:012d}.jpg")
    cv2.imwrite(str(img_path), mosaic)

    return {
        "id": id,
        "file_name": img_path.name,
        "coco_url": str(img_path),
        "height": mosaic.shape[0],
        "width": mosaic.shape[1],
        "bboxes": np.round(bboxes, 2),
        "category_ids": category_ids,
        "iscrowds": iscrowds,
        "original_img_ids": img_ids,
    }


def main(args):
    import functools
    import json
    import random
    from collections import defaultdict
    from concurrent.futures import ProcessPoolExecutor

    from tqdm import tqdm

    print("Reading coco file...")
    coco_file = json.load(open(args.coco_file))
    images, annotations, categories = (
        coco_file["images"],
        coco_file["annotations"],
        coco_file["categories"],
    )
    del coco_file

    imgid_to_anns = defaultdict(list)
    [imgid_to_anns[ann["image_id"]].append(ann) for ann in annotations]
    for img_dict in images:
        img_dict["annotations"] = imgid_to_anns[img_dict["id"]]
    del imgid_to_anns

    if args.shuffle:
        random.shuffle(images)
    images = [
        images[i : i + args.nrow * args.ncol] for i in range(0, len(images), args.nrow * args.ncol)
    ]
    if args.drop_last and (len(images[-1]) != args.nrow * args.ncol):
        images = images[:-1]

    args.output_dir.joinpath("images").mkdir()  # not allowed if 'images' exists
    worker_exec_partial = functools.partial(worker_exec, args)
    with ProcessPoolExecutor(max_workers=args.num_proc) as executor:
        images_new = list(
            tqdm(
                executor.map(worker_exec_partial, images, range(1, 1 + len(images))),
                total=len(images),
            )
        )

    annotations_new = []
    for img_dict in images_new:
        bboxes, category_ids, iscrowds = (
            img_dict.pop("bboxes"),
            img_dict.pop("category_ids"),
            img_dict.pop("iscrowds"),
        )
        assert len(bboxes) == len(category_ids)
        for bbox, category_id, iscrowd in zip(bboxes, category_ids, iscrowds):
            annotations_new.append(
                {
                    "id": len(annotations_new) + 1,
                    "image_id": img_dict["id"],
                    "area": np.round(bbox[-2] * bbox[-1], 2),
                    "bbox": bbox.tolist(),
                    "segmentation": [],
                    "category_id": category_id,
                    "iscrowd": iscrowd,
                }
            )

    json.dump(
        {
            "info": "The mosaic images and annotations are generated by the script from MosaicOS. ",
            "images": images_new,
            "annotations": annotations_new,
            "categories": categories,
        },
        open(args.output_dir.joinpath("annotations.json"), "w"),
    )

    if args.demo > 0:
        demo_save_dir = args.output_dir.joinpath("demo")
        demo_save_dir.mkdir()

        imgid_to_anns = defaultdict(list)
        [imgid_to_anns[ann["image_id"]].append(ann) for ann in annotations_new]
        for i in range(args.demo):
            img = cv2.imread(images_new[i]["coco_url"])

            for ann in imgid_to_anns[images_new[i]["id"]]:
                x, y, w, h = ann["bbox"]
                x, y, x2, y2 = round(x), round(y), round(x + w), round(y + h)
                img = cv2.rectangle(img, (x, y), (x2, y2), color=(0, 0, 255), thickness=2)

            cv2.imwrite(str(demo_save_dir.joinpath(f"{images_new[i]['id']:012d}.jpg")), img)


def parse_args():
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Image mosaicking")
    parser.add_argument("--coco-file", required=True, type=Path)
    parser.add_argument("--img-dir", default=Path("datasets/coco"), type=Path)
    parser.add_argument("--output-dir", default=Path("output_mosaics"), type=Path)
    parser.add_argument("--num-proc", default=1, type=int)
    parser.add_argument("--nrow", default=2, type=int)
    parser.add_argument("--ncol", default=2, type=int)
    parser.add_argument("--shuffle", action="store_true")
    parser.add_argument("--drop-last", action="store_true")
    parser.add_argument("--demo", default=0, type=int)

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.output_dir.mkdir(exist_ok=True)
    main(args)
