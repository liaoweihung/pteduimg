from pathlib import Path
import urllib.request
URL='https://data.fda.gov.tw/opendata/exportDataList.do?method=ExportData&InfoId=36&logType=5'
out=Path(__file__).resolve().parents[1]/'source'/'raw'/'tfda_drug_license_info36_20260711.zip'
out.parent.mkdir(parents=True, exist_ok=True)
urllib.request.urlretrieve(URL, out)
print(out)
