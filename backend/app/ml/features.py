# Label wording for the "why is this customer at risk" explanation. Must match the
# input columns in mlpart/train.py.

# (label when value <= training median, label when value > median, unit after the value)
VALUE_AWARE_LABELS = {
    "Tenure": ("short customer tenure", "long customer tenure", " months"),
    "DaySinceLastOrder": ("recent last order", "long time since last order", " days"),
    "CashbackAmount": ("low cashback earned", "high cashback earned", ""),
    "SatisfactionScore": ("low satisfaction score", "high satisfaction score", "/5"),
    "NumberOfAddress": ("few saved addresses", "many saved addresses", ""),
    "OrderCount": ("few orders placed", "many orders placed", ""),
    "WarehouseToHome": ("short delivery distance", "long delivery distance", ""),
}

# Marital status is a legitimate model input but a poor "reason" to show an admin.
NON_REASON_COLS = {"MaritalStatus"}
