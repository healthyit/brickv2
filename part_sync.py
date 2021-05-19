import logging
from context import Context
from entities.colours import Colours


def main():
    logging.info("[+] Part Sync")
    context = Context()
    colours = Colours(context)
    colours.sync_with_bricklink()
    # PartCategories(context)
    # parts = Parts(context, '2021-05-01')
    # parts.load_from_web('Minifigure, Weapon')
    # SetCategories(context)
    # sets = LSets(context)
    # sets.load_from_web()
    # part_colours = PartColours()
    # part_details = PartDetails()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    logging.getLogger("gnupg").setLevel(logging.WARNING)
    main()

