import subprocess
import nmcli

def runSubProc(args):
    import os
    po, pi = os.pipe()
    try:
        out = subprocess.check_output(args, stderr = pi)
        os.close(pi)
        os.close(po)
        return True, out
    except subprocess.CalledProcessError as e:
        out = os.read(po, 1<<12)
        os.close(pi)
        os.close(po)
        return False, nmcli.strip(out)

def getWifiInterface():
    fields = 'DEVICE,TYPE,STATE'
    args = ['env', 'nmcli', '-t', '-f', fields, 'device']
    ok, out = runSubProc(args)
    if ok:
        va =  nmcli.parse(out)
        r = {}
        for i in va:
            device, type, state = i
            if type == "wifi" and state != "unmanaged":
                r[device] = state
        return r
    else:
        return {"error": out}

def getEthernetInterface():
    fields = 'DEVICE,TYPE,STATE'
    args = ['env', 'nmcli', '-t', '-f', fields, 'device']
    ok, out = runSubProc(args)
    if ok:
        va =  nmcli.parse(out)
        r = {}
        for i in va:
            device, type, state = i
            if type == "ethernet" and state != "unmanaged":
                r[device] = state
        return r
    else:
        return {"error": out}

def getInterfaceDetail(iface):
    args = ['env', 'nmcli', '-t', 'device', 'show', iface]
    ok, out = runSubProc(args)
    if ok:
        va = nmcli.parseShow(out)
        r = {}
        r['general'] = {}
        for i in va:
            (k, v) = i
            if k.startswith('GENERAL'):
                if not r.get('general'):
                    r['general'] = {}
            elif k.startswith('IP4'):
                if not r.get('ipv4'):
                    r['ipv4'] = {}
            elif k.startswith('IP6'):
                if not r.get('ipv6'):
                    r['ipv6'] = {}

            if k == 'GENERAL.HWADDR':
                r['general']['hdaddr'] = v
            elif k == 'GENERAL.STATE':
                r['general']['state'] = v
            elif k == 'GENERAL.CONNECTION':
                r['general']['connection'] = v
            elif k.startswith('IP4.ADDRESS'):
                if not r['ipv4'].get('address'):
                    r['ipv4']['address'] = []
                r['ipv4']['address'].append(v)
            elif k.startswith('IP4.DNS'):
                if not r['ipv4'].get('dns'):
                    r['ipv4']['dns'] = []
                r['ipv4']['dns'].append(v)
            elif k.startswith('IP4.GATEWAY'):
                r['ipv4']['gateway'] = v
            elif k.startswith('IP6.ADDRESS'):
                if not r['ipv6'].get('address'):
                    r['ipv6']['address'] = []
                r['ipv6']['address'].append(v)
            elif k.startswith('IP6.GATEWAY'):
                r['ipv6']['gateway'] = v
            elif k.startswith('IP6.DNS'):
                if not r['ipv6'].get('dns'):
                    r['ipv6']['dns'] = []
                r['ipv6']['dns'].append(v)
            elif k == 'WIRED-PROPERTIES.CARRIER':
                r['wirestate'] = v

        return r
    else:
        return {"error", out}

def getScanResult():
    fields = 'SSID,MODE,CHAN,RATE,SIGNAL,SECURITY'
    args = ['env', 'nmcli', '-t', '-f', fields, 'device', 'wifi']
    ok, out = runSubProc(args)
    if ok:
        va = nmcli.parse(out)
        r = {}
        for i in va:
            ssid, mode, chan, rate, signal, enc = i
            r[ssid] = {"mode": mode, "channel": chan, "rate": rate, "signal": signal, "encryption": enc}
        return r
    else:
        return {"error": out}

def getWifiConnection():
    fields = 'NAME,UUID,TYPE,DEVICE'
    args = ['env', 'nmcli', '-t', '-f', fields, 'connection']
    ok, out = runSubProc(args)
    if ok:
        va =  nmcli.parse(out)
        r = {}
        for i in va:
            name, uuid, type, device = i
            if type == "802-11-wireless":
                r[uuid] = {"name": name, "device": device}
        return r
    else:
        return {"error": out}

def getEthernetConnection():
    fields = 'NAME,UUID,TYPE,DEVICE'
    args = ['env', 'nmcli', '-t', '-f', fields, 'connection']
    ok, out = runSubProc(args)
    if ok:
        va =  nmcli.parse(out)
        r = {}
        for i in va:
            name, uuid, type, device = i
            if type == "802-3-ethernet":
                r[uuid] = {"name": name, "device": device}
        return r
    else:
        return {"error": out}

def activateConnection(uuid, iface = None):
    if uuid == None:
        return {"error": "invalid parameter"}
    args = ['env', 'nmcli', 'connection', 'up', uuid]
    if iface:
        args.append("ifname")
        args.append(iface)
    ok, out = runSubProc(args)
    if ok:
        return {"msg": nmcli.strip(out)}
    else:
        return {"error": out}

def createWifiConnection(ssid, password = None, iface=None, name=None):
    timeout = '20'
    if ssid == None:
        return {"error": "invalid parameter"}
    args = ['env', 'nmcli', '--wait', timeout, 'device', 'wifi', 'connect', ssid]
    if password:
        args.append("password")
        args.append(password)
    if iface:
        args.append("ifname")
        args.append(iface)
    if name:
        args.append("name")
        args.append(name)
    ok, out = runSubProc(args)
    if ok:
        return {"msg": nmcli.strip(out)}
    else:
        return {"error": out}

def deleteConnection(uuid):
    if uuid == None:
        return {"error": "invalid parameter"}
    args = ['env', 'nmcli', 'connection', 'delete', uuid]
    ok, out = runSubProc(args)
    if ok:
        return {"msg": "ok"}
    else:
        return {"error": out}

def disconnect(iface):
    if iface == None:
        return {"error": "invalid parameter"}
    args = ['env', 'nmcli', 'device', 'disconnect', iface]
    ok, out = runSubProc(args)
    if ok:
        return {"msg": "ok"}
    else:
        return {"error": out}

if __name__ == "__main__":
    print(getInterfaceDetail('eth0'))
    print(getWifiInterface())
    print(getEthernetInterface())
    print(getScanResult())
    print(getWifiConnection())
