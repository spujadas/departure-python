import os
from zeep import Client
from zeep import xsd


from . import commons


def soap_client(ldb_token: str =None):
    if ldb_token is None:  # get from env vars by default
        try:
            ldb_token = os.environ["LDB_TOKEN"]
        except KeyError:
            raise commons.NationalRailException("missing env var LDB_TOKEN") from KeyError

    header = xsd.Element(
        "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken",
        xsd.ComplexType(
            [
                xsd.Element(
                    "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}"
                    "TokenValue",
                    xsd.String(),
                ),
            ]
        ),
    )

    wsdl = (
        "http://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-10-01"
    )

    return {
        'headers': [header(TokenValue=ldb_token)],
        'client': Client(wsdl=wsdl)
    }


def get_departure_board_with_details(station_id: str, num_rows: int = 10):
    soap_client_dict = soap_client()

    return soap_client_dict['client'].service.GetDepBoardWithDetails(
        crs=station_id, numRows=num_rows, _soapheaders=soap_client_dict['headers']
    )
