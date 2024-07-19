## Buffer class used in both position sizing and portfolio
import pandas as pd
import numpy as np

from sysdata.config.configdata import Config
from syslogging.logger import *
from syscore.constants import arg_not_supplied


def calculate_actual_buffers(
    buffers: pd.DataFrame, cap_multiplier: pd.Series
) -> pd.DataFrame:
    """
    Used when rescaling capital for accumulation
    """

    cap_multiplier = cap_multiplier.reindex(buffers.index).ffill()
    cap_multiplier = pd.concat([cap_multiplier, cap_multiplier], axis=1)
    cap_multiplier.columns = buffers.columns

    actual_buffers_for_position = buffers * cap_multiplier

    return actual_buffers_for_position


def apply_buffers_to_position(position: pd.Series, buffer: pd.Series) -> pd.DataFrame:
    top_position = position.ffill() + buffer.ffill()
    bottom_position = position.ffill() - buffer.ffill()

    pos_buffers = pd.concat([top_position, bottom_position], axis=1)
    pos_buffers.columns = ["top_pos", "bot_pos"]

    return pos_buffers


def calculate_buffers(
    instrument_code: str,
    position: pd.Series,
    config: Config,
    vol_scalar: pd.Series,
    instr_weights: pd.DataFrame = arg_not_supplied,
    idm: pd.Series = arg_not_supplied,
    log=get_logger(""),
) -> pd.Series:
    log.debug(
        "Calculating buffers for %s" % instrument_code,
        instrument_code=instrument_code,
    )

    buffer_method = config.buffer_method

    if buffer_method == "forecast":
        log.debug(
            "Calculating forecast method buffers for %s" % instrument_code,
            instrument_code=instrument_code,
        )
        if instr_weights is arg_not_supplied:
            instr_weight_this_code = arg_not_supplied
        else:
            instr_weight_this_code = instr_weights[instrument_code]

        buffer = get_forecast_method_buffer(
            instr_weight_this_code=instr_weight_this_code,
            vol_scalar=vol_scalar,
            idm=idm,
            position=position,
            config=config,
        )

    elif buffer_method == "position":
        log.debug(
            "Calculating position method buffer for %s" % instrument_code,
            instrument_code=instrument_code,
        )

        buffer = get_position_method_buffer(config=config, position=position)
    elif buffer_method == "none":
        log.debug(
            "None method, no buffering for %s" % instrument_code,
            instrument_code=instrument_code,
        )

        buffer = get_buffer_if_not_buffering(position=position)
    else:
        log.critical("Buffer method %s not recognised - not buffering" % buffer_method)
        buffer = get_buffer_if_not_buffering(position=position)

    return buffer


def get_forecast_method_buffer(
    position: pd.Series,
    vol_scalar: pd.Series,
    config: Config,
    instr_weight_this_code: pd.Series = arg_not_supplied,
    idm: pd.Series = arg_not_supplied,
) -> pd.Series:
    """
    Gets the buffers for positions, using proportion of average forecast method


    :param instrument_code: instrument to get values for
    :type instrument_code: str

    :returns: Tx1 pd.DataFrame
    """

    buffer_size = config.buffer_size

    buffer = _calculate_forecast_buffer_method(
        buffer_size=buffer_size,
        position=position,
        idm=idm,
        instr_weight_this_code=instr_weight_this_code,
        vol_scalar=vol_scalar,
    )

    return buffer


def get_position_method_buffer(
    position: pd.Series,
    config: Config,
) -> pd.Series:
    """
    Gets the buffers for positions, using proportion of position method

    """

    buffer_size = config.buffer_size
    abs_position = abs(position)

    buffer = abs_position * buffer_size

    buffer.columns = ["buffer"]

    return buffer


def get_buffer_if_not_buffering(position: pd.Series) -> pd.Series:
    EPSILON_POSITION = 0.001
    buffer = pd.Series([EPSILON_POSITION] * position.shape[0], index=position.index)

    return buffer


def get_buffered_position(
    optimal_position: pd.Series,
    pos_buffers: pd.DataFrame,
    roundpositions: bool = True,
    buffer_method: str = None,
    trade_to_edge: bool = True,
    log=get_logger(""),
) -> pd.Series:
    """
    Get a series of buffered positions given the optimal positions and buffers. Works
    at system and subsystem levels

    :param optimal_position: pd.Series of optimal postions
    :param pos_buffers: pd.Dataframe of buffers
    :param roundpositions: whether to round positions (boolean)
    :param buffer_method: str representing the configured buffer method. One of
        'position', 'forecast', or 'none'
    :param trade_to_edge: whether we trade to the edge of the buffer. The
        alternative is to trade to the mid (boolean)

    :return:
    """
    if buffer_method == "none":
        if roundpositions:
            return optimal_position.round()
        else:
            return optimal_position

    log.debug("Calculating buffered positions")

    buffered_position = _apply_buffer(
        optimal_position,
        pos_buffers,
        trade_to_edge=trade_to_edge,
        roundpositions=roundpositions,
    )

    return buffered_position


def _calculate_forecast_buffer_method(
    position: pd.Series,
    buffer_size: float,
    vol_scalar: pd.Series,
    idm: pd.Series = arg_not_supplied,
    instr_weight_this_code: pd.Series = arg_not_supplied,
):
    if instr_weight_this_code is arg_not_supplied:
        instr_weight_this_code_indexed = 1.0
    else:
        instr_weight_this_code_indexed = instr_weight_this_code.reindex(
            position.index
        ).ffill()

    if idm is arg_not_supplied:
        idm_indexed = 1.0
    else:
        idm_indexed = idm.reindex(position.index).ffill()

    vol_scalar_indexed = vol_scalar.reindex(position.index).ffill()

    average_position = abs(
        vol_scalar_indexed * instr_weight_this_code_indexed * idm_indexed
    )

    buffer = average_position * buffer_size

    return buffer


def _apply_buffer(
    optimal_position: pd.Series,
    pos_buffers: pd.DataFrame,
    trade_to_edge: bool = False,
    roundpositions: bool = False,
) -> pd.Series:
    """
    Apply a buffer to a position

    If position is outside the buffer, we either trade to the edge of the
    buffer, or to the optimal

    If we're rounding positions, then we floor and ceiling the buffers.

    :param position: optimal position
    :type position: pd.Series

    :param pos_buffers:
    :type pos_buffers: Tx2 pd.dataframe, top_pos and bot_pos

    :param trade_to_edge: Trade to the edge (TRue) or the optimal (False)
    :type trade_to_edge: bool

    :param round_positions: Produce rounded positions
    :type round_positions: bool

    :returns: pd.Series
    """

    pos_buffers = pos_buffers.ffill()
    use_optimal_position = optimal_position.ffill()

    top_pos = pos_buffers.top_pos
    bot_pos = pos_buffers.bot_pos

    if roundpositions:
        use_optimal_position = use_optimal_position.round()
        top_pos = top_pos.round()
        bot_pos = bot_pos.round()

    current_position = use_optimal_position.values[0]
    if np.isnan(current_position):
        current_position = 0.0

    buffered_position_list = [current_position]

    for idx in range(len(optimal_position.index))[1:]:
        current_position = _apply_buffer_single_period(
            current_position,
            float(use_optimal_position.values[idx]),
            float(top_pos.values[idx]),
            float(bot_pos.values[idx]),
            trade_to_edge=trade_to_edge,
        )
        buffered_position_list.append(current_position)

    buffered_position = pd.Series(buffered_position_list, index=optimal_position.index)

    return buffered_position


def _apply_buffer_single_period(
    last_position, optimal_position, top_pos, bot_pos, trade_to_edge
):
    """
    Apply a buffer to a position, single period

    If position is outside the buffer, we either trade to the edge of the
    buffer, or to the optimal

    :param last_position: last position we had
    :type last_position: float

    :param optimal_position: ideal position
    :type optimal_position: float

    :param top_pos: top of buffer
    :type top_pos: float

    :param bot_pos: bottom of buffer
    :type bot_pos: float

    :param trade_to_edge: Trade to the edge (TRue) or the optimal (False)
    :type trade_to_edge: bool

    :returns: float
    """

    if np.isnan(top_pos) or np.isnan(bot_pos) or np.isnan(optimal_position):
        return last_position

    if last_position > top_pos:
        if trade_to_edge:
            return top_pos
        else:
            return optimal_position
    elif last_position < bot_pos:
        if trade_to_edge:
            return bot_pos
        else:
            return optimal_position
    else:
        return last_position
