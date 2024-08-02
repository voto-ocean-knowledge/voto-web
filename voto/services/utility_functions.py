def seconds_to_pretty(seconds):
    total_days = int(seconds / (24 * 60 * 60))
    years = total_days // 365
    days = total_days - (365 * years)
    if years:
        time_str = f"{years} years {days} days"
    else:
        time_str = f"{days} days"
    return time_str


def m_to_naut_miles(m):
    miles = int(m * 0.00053996)
    return "{:,}".format(miles)


def fix_erddap_unicode(erddap_str):
    """
    Fixes strings ISO/IEC 8859-1 (latin1) that have been mangled by ERDDAP.
    ie the bottom half of https://en.wikipedia.org/wiki/ISO/IEC_8859-1
    This is a very ugly function made from trial and error. It fixes the common latin characters in datasets from ERDDAP
    ( à  á  â  ã  ä  å  æ  ç  è  é  ê  ë  ì  etc.) but will likely break on other input.
    """
    # ERDDAP adds extra shift points for characters in the latter half of the table. I think because it makes 7 bit
    # chars with 2 bytes(?) rather than the expected 8 bits.
    if "\\u00c2" not in erddap_str and "\\u00c3" not in erddap_str:
        return erddap_str
    # We replace the two shift codes with unique symbols
    if "\\u00c2" in erddap_str:
        erddap_str = erddap_str.replace("\\u00c2", "𐆠")
    if "\\u00c3" in erddap_str:
        erddap_str = erddap_str.replace("\\u00c3", "𐆜")
    replacement_dict = {}
    replacement_dict_nopre = {}
    shift = 0
    prefig = ""
    for i in range(len(erddap_str)):
        if erddap_str[i] == "𐆠":
            shift = 0
            prefig = "𐆠"
        if erddap_str[i] == "𐆜":
            shift = 2**6
            prefig = "𐆜"
        # look for ERDDAP's ISO/IEC 8859-1 control sequences
        if erddap_str[i] == "\\" and erddap_str[i + 1] == "u":
            unicode_point = int(erddap_str[i + 2 : i + 6], 16)
            new_str = hex(unicode_point + shift)
            if prefig:
                replacement_dict[prefig + erddap_str[i : i + 6]] = f"\\{new_str[1:]}"
            else:
                replacement_dict_nopre[
                    prefig + erddap_str[i : i + 6]
                ] = f"\\{new_str[1:]}"
            prefig = ""
    # First replace the two character sequences, before the one character sequences
    for key, val in replacement_dict.items():
        erddap_str = erddap_str.replace(key, val)
    for key, val in replacement_dict_nopre.items():
        erddap_str = erddap_str.replace(key, val)
    return erddap_str.encode("utf-8").decode("unicode-escape")


def fix_df_erddap_str(df):
    """
    Fixes Pandas Dataframes which have string values mangled by ERDDAP
    """
    for col in df.columns:
        if str(df[col].dtype) not in ["string", "object"]:
            continue
        unique_strings = df[col].astype(str).unique()
        if "\\u" not in "".join(unique_strings):
            continue
        for accent_str in unique_strings:
            if "\\u" not in accent_str:
                continue
            corr_str = fix_erddap_unicode(accent_str)
            df = df.replace(accent_str, corr_str)
    return df
