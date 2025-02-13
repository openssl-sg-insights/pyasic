#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Union, List
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import time
import json
import copy

from .error_codes import X19Error, WhatsminerError, BraiinsOSError, InnosiliconError


@dataclass
class MinerData:
    """A Dataclass to standardize data returned from miners (specifically `AnyMiner().get_data()`)

    Attributes:
        ip: The IP of the miner as a str.
        datetime: The time and date this data was generated.
        model: The model of the miner as a str.
        hostname: The network hostname of the miner as a str.
        hashrate: The hashrate of the miner in TH/s as a float.
        left_board_hashrate: The hashrate of the left board of the miner in TH/s as a float.
        center_board_hashrate: The hashrate of the center board of the miner in TH/s as a float.
        right_board_hashrate: The hashrate of the right board of the miner in TH/s as a float.
        temperature_avg: The average temperature across the boards.  Calculated automatically.
        env_temp: The environment temps as a float.
        left_board_temp: The temp of the left PCB as an int.
        left_board_chip_temp: The temp of the left board chips as an int.
        center_board_temp: The temp of the center PCB as an int.
        center_board_chip_temp: The temp of the center board chips as an int.
        right_board_temp: The temp of the right PCB as an int.
        right_board_chip_temp: The temp of the right board chips as an int.
        wattage: Current power draw of the miner as an int.
        wattage_limit: Power limit of the miner as an int.
        fan_1: The speed of the first fan as an int.
        fan_2: The speed of the second fan as an int.
        fan_3: The speed of the third fan as an int.
        fan_4: The speed of the fourth fan as an int.
        fan_psu: The speed of the PSU on the fan if the miner collects it.
        left_chips: The number of chips online in the left board as an int.
        center_chips: The number of chips online in the left board as an int.
        right_chips: The number of chips online in the left board as an int.
        total_chips: The total number of chips on all boards.  Calculated automatically.
        ideal_chips: The ideal number of chips in the miner as an int.
        percent_ideal: The percent of total chips out of the ideal count.  Calculated automatically.
        nominal: Whether the number of chips in the miner is nominal.  Calculated automatically.
        pool_split: The pool split as a str.
        pool_1_url: The first pool url on the miner as a str.
        pool_1_user: The first pool user on the miner as a str.
        pool_2_url: The second pool url on the miner as a str.
        pool_2_user: The second pool user on the miner as a str.
        errors: A list of errors on the miner.
        fault_light: Whether or not the fault light is on as a boolean.
        efficiency: Efficiency of the miner in J/TH (Watts per TH/s).  Calculated automatically.
    """

    ip: str
    datetime: datetime = None
    mac: str = "00:00:00:00:00:00"
    model: str = "Unknown"
    hostname: str = "Unknown"
    hashrate: float = 0
    left_board_hashrate: float = 0.0
    center_board_hashrate: float = 0.0
    right_board_hashrate: float = 0.0
    temperature_avg: int = field(init=False)
    env_temp: float = -1.0
    left_board_temp: int = -1
    left_board_chip_temp: int = -1
    center_board_temp: int = -1
    center_board_chip_temp: int = -1
    right_board_temp: int = -1
    right_board_chip_temp: int = -1
    wattage: int = -1
    wattage_limit: int = -1
    fan_1: int = -1
    fan_2: int = -1
    fan_3: int = -1
    fan_4: int = -1
    fan_psu: int = -1
    left_chips: int = 0
    center_chips: int = 0
    right_chips: int = 0
    total_chips: int = field(init=False)
    ideal_chips: int = 1
    percent_ideal: float = field(init=False)
    nominal: int = field(init=False)
    pool_split: str = "0"
    pool_1_url: str = "Unknown"
    pool_1_user: str = "Unknown"
    pool_2_url: str = ""
    pool_2_user: str = ""
    errors: List[
        Union[WhatsminerError, BraiinsOSError, X19Error, InnosiliconError]
    ] = field(default_factory=list)
    fault_light: Union[bool, None] = None
    efficiency: int = field(init=False)

    def __post_init__(self):
        self.datetime = datetime.now(timezone.utc).astimezone()

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(f"{item}")

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __iter__(self):
        return iter([item for item in self.asdict()])

    def __truediv__(self, other):
        return self // other

    def __floordiv__(self, other):
        cp = copy.deepcopy(self)
        for key in self:
            item = getattr(self, key)
            if isinstance(item, int):
                setattr(cp, key, item // other)
            if isinstance(item, float):
                setattr(cp, key, round(item / other, 2))
        return cp

    def __add__(self, other):
        if not isinstance(other, MinerData):
            raise TypeError("Cannot add MinerData to non MinerData type.")
        cp = copy.deepcopy(self)
        for key in self:
            item = getattr(self, key)
            other_item = getattr(other, key)
            if item is None:
                item = 0
            if other_item is None:
                other_item = 0

            if isinstance(item, int):
                setattr(cp, key, item + other_item)
            if isinstance(item, float):
                setattr(cp, key, item + other_item)
            if isinstance(item, str):
                setattr(cp, key, "")
            if isinstance(item, list):
                setattr(cp, key, item + other_item)
            if isinstance(item, bool):
                setattr(cp, key, item & other_item)
        return cp

    @property
    def total_chips(self):  # noqa - Skip PyCharm inspection
        return self.right_chips + self.center_chips + self.left_chips

    @total_chips.setter
    def total_chips(self, val):
        pass

    @property
    def nominal(self):  # noqa - Skip PyCharm inspection
        return self.ideal_chips == self.total_chips

    @nominal.setter
    def nominal(self, val):
        pass

    @property
    def percent_ideal(self):  # noqa - Skip PyCharm inspection
        return round((self.total_chips / self.ideal_chips) * 100)

    @percent_ideal.setter
    def percent_ideal(self, val):
        pass

    @property
    def temperature_avg(self):  # noqa - Skip PyCharm inspection
        total_temp = 0
        temp_count = 0
        for temp in [
            self.left_board_chip_temp,
            self.center_board_chip_temp,
            self.right_board_chip_temp,
        ]:
            if temp and not temp == -1:
                total_temp += temp
                temp_count += 1
        if not temp_count > 0:
            return 0
        return round(total_temp / temp_count)

    @temperature_avg.setter
    def temperature_avg(self, val):
        pass

    @property
    def efficiency(self):  # noqa - Skip PyCharm inspection
        if self.hashrate == 0:
            return 0
        return round(self.wattage / self.hashrate)

    @efficiency.setter
    def efficiency(self, val):
        pass

    def asdict(self) -> dict:
        """Get this dataclass as a dictionary.

        Returns:
            A dictionary version of this class.
        """
        return asdict(self)

    def as_json(self) -> str:
        """Get this dataclass as JSON.

        Returns:
            A JSON version of this class.
        """
        data = self.asdict()
        data["datetime"] = str(int(time.mktime(data["datetime"].timetuple())))
        return json.dumps(data)

    def as_csv(self) -> str:
        """Get this dataclass as CSV.

        Returns:
            A CSV version of this class with no headers.
        """
        data = self.asdict()
        data["datetime"] = str(int(time.mktime(data["datetime"].timetuple())))
        errs = []
        for error in data["errors"]:
            errs.append(error["error_message"])
        data["errors"] = "; ".join(errs)
        data_list = [str(data[item]) for item in data]
        return ",".join(data_list)

    def as_influxdb(self, measurement_name: str = "miner_data") -> str:
        """Get this dataclass as [influxdb line protocol](https://docs.influxdata.com/influxdb/v2.4/reference/syntax/line-protocol/).

        Parameters:
            measurement_name: The name of the measurement to insert into in influxdb.

        Returns:
            A influxdb line protocol version of this class.
        """
        tag_data = [measurement_name]
        field_data = []

        tags = ["ip", "mac", "model", "hostname"]
        for attribute in self:
            if attribute in tags:
                escaped_data = self[attribute].replace(" ", "\\ ")
                tag_data.append(f"{attribute}={escaped_data}")
                continue
            if isinstance(self[attribute], str):
                field_data.append(f'{attribute}="{self[attribute]}"')
                continue
            if isinstance(self[attribute], bool):
                field_data.append(f"{attribute}={str(self[attribute]).lower()}")
                continue
            if isinstance(self[attribute], int):
                field_data.append(f"{attribute}={self[attribute]}")
                continue
            if isinstance(self[attribute], float):
                field_data.append(f"{attribute}={self[attribute]}")
                continue
            if attribute == "fault_light" and not self[attribute]:
                field_data.append(f"{attribute}=false")
                continue
            if attribute == "errors":
                for idx, item in enumerate(self[attribute]):
                    field_data.append(f'error_{idx+1}="{item.error_message}"')

        tags_str = ",".join(tag_data)
        field_str = ",".join(field_data)
        timestamp = str(int(time.mktime(self.datetime.timetuple()) * 1e9))

        return " ".join([tags_str, field_str, timestamp])
