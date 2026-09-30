from typing import List, Dict


def build_comic_layout(panels: List[Dict], image_paths: List[str]) -> List[Dict]:
    layout = []
    for panel, image_path in zip(panels, image_paths):
        item = dict(panel)
        item["image_path"] = image_path
        layout.append(item)
    return layout
