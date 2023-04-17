#!/usr/bin/env python3

import requests
import json
import attr

user_agent = "poe-vial-upgrades/1.0"

ses = requests.Session()
ses.headers.update({"user-agent" : user_agent})


@attr.s
class UpgradePath (object):
    start_item     = attr.ib()
    vial           = attr.ib()
    upgraded_item  = attr.ib()

    start_price    = attr.ib(default=None)
    vial_price     = attr.ib(default=-1)
    upgraded_price = attr.ib(default=None)

    def get_gain(self):
        if self.vial_price == -1:
            return -999
        else:
            return self.upgraded_price - (self.start_price + self.vial_price)


def get_current_league():
    r = ses.get("https://poe.ninja/api/data/getindexstate")
    return json.loads(r.text)["economyLeagues"][0]["name"]


def poe_ninja_item_overview(league, type_):
    r = ses.get("https://poe.ninja/api/data/ItemOverview?league={}&type={}&language=en".format(league, type_))
    return json.loads(r.text)["lines"]


def main():
    league = get_current_league()
    print("{} League\n".format(league))

    upgrades = [
        UpgradePath("Apep's Slumber",             "Awakening",     "Apep's Supremacy"),
        UpgradePath("Coward's Chains",            "Consequence",   "Coward's Legacy"),
        UpgradePath("Architect's Hand",           "Dominance",     "Slavedriver's Hand"),
        UpgradePath("Story of the Vaal",          "Fate",          "Fate of the Vaal"),
        UpgradePath("Soul Catcher",               "the Ghost",     "Soul Ripper"),
        UpgradePath("Dance of the Offered",       "the Ritual",    "Omeyocan"),
        UpgradePath("Sacrificial Heart",          "Sacrifice",     "Zerphi's Heart"),
        UpgradePath("Mask of the Spirit Drinker", "Summoning",     "Mask of the Stitched Demon"),
        UpgradePath("Tempered Flesh",             "Transcendence", "Transcendent Flesh"),
        UpgradePath("Tempered Mind",              "Transcendence", "Transcendent Mind"),
        UpgradePath("Tempered Spirit",            "Transcendence", "Transcendent Spirit")
    ]

    temple_items = set()
    for u in upgrades:
        temple_items.add(u.start_item)
        temple_items.add(u.upgraded_item)

    for vial in poe_ninja_item_overview(league, "Vial"):
        for upgrade in upgrades:
            if upgrade.vial in vial["name"]:
                upgrade.vial_price = vial["chaosValue"]

    prices = {}
    for type_ in ("UniqueArmour", "UniqueWeapon", "UniqueAccessory", "UniqueJewel", "UniqueFlask"):
        for item in poe_ninja_item_overview(league, type_):
            if item["name"] in temple_items:
                prices[item["name"]] = item["chaosValue"]

    widths = [0, 0, 0, 0, 0, 0, 0]
    prec = 0
    for u in upgrades:
        u.start_price    = prices[u.start_item]
        u.upgraded_price = prices[u.upgraded_item]

        for i,a in enumerate(attr.fields(UpgradePath)):
            val = getattr(u, a.name)
            if type(val) is str:
                widths[i] = max(widths[i], len(val))
            elif type(val) is float:
                widths[i] = max(widths[i], len(f"{val:.{prec}f}"))

        widths[-1] = max(widths[-1], len(f"{u.get_gain():.{prec}f}") + 1)

    print("{:<{widths[0]}}     {:<{widths[1]}}     {:<{widths[2]}}  |  {:>{widths[3]}}     {:>{widths[4]}}      {:>{widths[5]}}     {:>{widths[6]}} ".format("Start Item", "Vial", "Upgraded Item", "S", "V", "U", "d", widths=widths))

    for i,w in enumerate(widths):
        print("-" * w, end="")
        if i == 2:
            print("--+--", end="")
        elif i == 4:
            print("-" * 6, end="")
        elif i == 6:
            print("-", end="")
        else:
            print("-" * 5, end="")
    print()

    for u in sorted(upgrades, key=lambda x: x.get_gain(), reverse=True):
        print(f"{u.start_item:<{widths[0]}}  +  {u.vial:<{widths[1]}}  =  {u.upgraded_item:<{widths[2]}}  |  {u.start_price:>{widths[3]}.{prec}f}  +  {u.vial_price:>{widths[4]}.{prec}f}  ->  {u.upgraded_price:>{widths[5]}.{prec}f}    ({u.get_gain():>+{widths[6]}.{prec}f})")


if __name__ == "__main__":
    main()
