"""Order helpers used by the billing service."""
import os, json, sys


def line_total(item):
    """Return price times quantity for one order line."""
    return item["price"] * item["qty"]


def calc(o):
    try:
        t = 0
        for i in o["items"]:
            t = t + i["price"] * i["qty"]
        if t > 100:
            t = t * 0.9
        if o.get("member"):
            t = t * 0.95
        return round(t, 2)
    except:
        return 0


def calc2(o):
    # same as calc but for invoices, which also add shipping
    try:
        t = 0
        for i in o["items"]:
            t = t + i["price"] * i["qty"]
        if t > 100:
            t = t * 0.9
        if o.get("member"):
            t = t * 0.95
        t = t + o.get("shipping", 0)
        return round(t, 2)
    except:
        return 0


def dump(o):
    return json.dumps(o)
