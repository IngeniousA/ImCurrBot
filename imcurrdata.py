import appsettings
import gspread
import random
import string
import os
import blowfish
from oauth2client.service_account import ServiceAccountCredentials

scope = [appsettings.scope, appsettings.scope2]
creds = ServiceAccountCredentials.from_json_keyfile_name(appsettings.creds, scope)
client = gspread.authorize(creds)


def setfile(telid, filename):
    datasheet = client.open(appsettings.datash).sheet1
    ind = datasheet.col_values(1).index(str(telid)) + 1
    datasheet.update_cell(ind, 2, filename)


def setkey(telid, key):
    datasheet = client.open(appsettings.datash).sheet1
    ind = datasheet.col_values(1).index(str(telid)) + 1
    datasheet.update_cell(ind, 3, key)


def init(telid):
    datasheet = client.open(appsettings.datash).sheet1
    if datasheet.col_values(1).count(str(telid)) == 0:
        datasheet.insert_row([str(telid), "0"], len(datasheet.col_values(1)) + 1)
    else:
        setkey(telid, "")
        setfile(telid, "0")


def getfile(telid):
    datasheet = client.open(appsettings.datash).sheet1
    ind = datasheet.col_values(1).index(str(telid)) + 1
    return datasheet.cell(ind, 2).value


def getkey(telid):
    datasheet = client.open(appsettings.datash).sheet1
    ind = datasheet.col_values(1).index(str(telid)) + 1
    return datasheet.cell(ind, 3).value


def randstr(size=9, chars=string.ascii_lowercase + string.digits):
    cand = ''.join(random.choice(chars) for _ in range(size))
    return cand


def launch(telid):
    src = appsettings.cache + "\\" + getfile(telid)
    name, ext = os.path.splitext(src)
    key = getkey(telid)
    bfish = blowfish.Cipher(key.encode())
    if ext == ".ictg":
        rawf = open(src, "rb")
        raw = rawf.read()
        rawf.close()
        decr = b"".join(bfish.decrypt_ecb_cts(raw))
        deco = open(name + ".dec", "wb")
        deco.write(decr)
        deco.close()
        return name + ".dec"
    else:
        rawf = open(src, "rb")
        raw = rawf.read()
        rawf.close()
        encr = b"".join(bfish.encrypt_ecb_cts(raw))
        enco = open(name + ".ictg", "wb")
        enco.write(encr)
        enco.close()
        return name + ".ictg"


def clear(telid):
    name, ext = os.path.splitext(getfile(telid))
    if ext == ".ictg":
        os.remove(appsettings.cache + "\\" + name + ext)
    else:
        os.remove(appsettings.cache + "\\" + name + ext)
    setfile(telid, "0")
    setkey(telid, "")