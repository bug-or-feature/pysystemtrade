import logging.config

COMPONENT_LOG_LABEL = "component"
TYPE_LOG_LABEL = "type"
STAGE_LOG_LABEL = "stage"
CLIENTID_LOG_LABEL = "clientid"
BROKER_LOG_LABEL = "broker"
STRATEGY_NAME_LOG_LABEL = "strategy_name"
CURRENCY_CODE_LOG_LABEL = "currency_code"
INSTRUMENT_CODE_LOG_LABEL = "instrument_code"
CONTRACT_DATE_LOG_LABEL = "contract_date"
ORDER_ID_LOG_LABEL = "order_id"
INSTRUMENT_ORDER_ID_LABEL = "instrument_order_id"
CONTRACT_ORDER_ID_LOG_LABEL = "contract_order_id"
BROKER_ORDER_ID_LOG_LABEL = "broker_order_id"


ALLOWED_LOG_ATTRIBUTES = [
    TYPE_LOG_LABEL,
    COMPONENT_LOG_LABEL,
    STAGE_LOG_LABEL,
    CURRENCY_CODE_LOG_LABEL,
    INSTRUMENT_CODE_LOG_LABEL,
    CONTRACT_DATE_LOG_LABEL,
    ORDER_ID_LOG_LABEL,
    STRATEGY_NAME_LOG_LABEL,
    INSTRUMENT_ORDER_ID_LABEL,
    CONTRACT_ORDER_ID_LOG_LABEL,
    BROKER_ORDER_ID_LOG_LABEL,
    BROKER_LOG_LABEL,
    CLIENTID_LOG_LABEL,
]

class DynamicAttributeLogger(logging.LoggerAdapter):
    def __init__(self, logger, attributes) -> None:
        self._check_attributes(attributes)
        super().__init__(logger, attributes)

    def process(self, msg, kwargs):
        attrs = dict()
        new_kwargs = dict()

        method = kwargs.pop("method", "overwrite")
        if method not in ["clear", "preserve", "overwrite", "temp"]:
            raise ValueError(f"Invalid value for 'method': {method}")

        for k, v in kwargs.items():
            if k in ALLOWED_LOG_ATTRIBUTES:
                attrs[k] = v
            else:
                new_kwargs[k] = v

        """
        Four possible ways to deal with attributes
        1. temp: passed values overwrite existing for one message, then discarded
        2. clear:  clear existing, use passed values
        3. preserve: merge with existing values preserved
        4. overwrite: merge with existing values overwritten
        """
        if method == "temp":
            if self.extra:
                return "%s %s" % ({**self.extra, **attrs}, msg), new_kwargs
            else:
                return "%s %s" % (attrs, msg), new_kwargs
        else:
            merged = self._merge_attributes(method, attrs)
            new_kwargs["extra"] = merged
            self.extra = merged

            if self.extra:
                return "%s %s" % (self.extra, msg), new_kwargs
            else:
                return "%s" % msg, new_kwargs

    def _merge_attributes(self, method, attributes):
        if not self.extra or method == "clear":
            merged = attributes
        elif method == "preserve":
            merged = {**attributes, **self.extra}
        else:
            merged = {**self.extra, **attributes}

        return merged

    def _check_attributes(self, attributes: dict):
        if attributes:
            bad_attributes = self._get_list_of_disallowed_attributes(attributes)
            if len(bad_attributes) > 0:
                raise Exception(
                    "Attributes %s not allowed in log" % str(bad_attributes)
                )

    def _get_list_of_disallowed_attributes(self, attributes: dict) -> list:
        attr_keys = list(attributes.keys())
        not_okay = [
            attribute_name
            for attribute_name in attr_keys
            if attribute_name not in ALLOWED_LOG_ATTRIBUTES
        ]
        return not_okay
