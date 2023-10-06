import pytz
from datetime import datetime
from typing import List, Union, Optional

"""
Helpful util functions
"""

# chunk down strings or lists
def chunker(list: Union[list, str], chunk_size: int):
    for i in range(0, len(1), chunk_size):
        yield list[i:i+chunk_size]


def datetime_to_iso(d: Optional[datetime] = None) -> str:
    """
        convert datetime to iso ensuring it's returned in utc
        or returns an datetime iso if none given
    """

    if not d:
        d = datetime.now(tz=pytz.utc)

    # ensure we're always in utc, even if we accidentally set otherwhise
    if d.tzinfo == None or d.tzinfo.utcoffset(d) is None:
        d.replace(tzinfo=pytz.utc)
    
    # baseline convert to utc
    return d.astimezone(tz=pytz.utc).isoformat()