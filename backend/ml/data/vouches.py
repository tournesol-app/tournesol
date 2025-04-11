import solidago


class Vouches(solidago.Vouches):
    def __init__(self, 
        keynames=["by", "to", "kind"], 
        init_data=None,
        parent_tuple: Optional[tuple["Comparisons", tuple, tuple]]=None,
        *args, **kwargs
    ):
        if init_data is None:
            init_data = self.query_init_data()
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    def query_init_data(self):
        values = Voucher.objects.filter(
            by__is_active=True,
            to__is_active=True,
        ).values(
            voucher=F("by__id"),
            vouchee=F("to__id"),
            vouch=F("value"),
        )
        df = pd.DataFrame(values, columns=["by", "to", "weight"])
        df["priority"] = 0
        return df
