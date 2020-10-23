import os
import re
import asyncio
from dotenv import load_dotenv
from subprocess import Popen, PIPE, getstatusoutput

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
myMacAdressesIPV4 = os.getenv('MACADRESSES')
myIPV6 = os.getenv('IPV6ADDRESSES')

interface = "wlp5s0" # you need to adapt this
# ping ff02::1%inferface search for ipv6

print("EMail",EMAIL)

async def main():
    
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)

    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    # Retrieve all the MSS310 devices that are registered on this account
    await manager.async_device_discovery()
    plugs = manager.find_devices(device_type="mss210")
    # Setup the HTTP client API from user-password
  
    
    if len(plugs) < 1:
        print("No MSS310 plugs found...")
    else:
        # Turn it on channel 0
        # Note that channel argument is optional for MSS310 as they only have one channel
        dev = plugs[0]
        
        # The first time we play with a device, we must update its status
        await dev.async_update()
        ## arp scan 
        #pid = Popen(["arp-scan","--interface=" + interface, "--localnet", "-r 10"], stdout=PIPE) 
        # need to be adapted to your bandwith 192.168.178.*
        # pid = Popen(["nmap",  "-sP", "-PE", "-PA21,23,80,3389","192.168.178.*"], stdout=PIPE)
        # s = str(pid.communicate()[0])
        # p = re.compile(r'(?:[0-9a-fA-F]:?){12}')
        # scannedMac = re.findall(p, s)
        # print("must have: ", myMacAdressesIPV4)
        # print("mac", scannedMac)
        # if any( i for i in scannedMac if i.lower() in myMacAdressesIPV4):
        # # We can now start playing with that
        #     print(f"Turning on {dev.name}...")
        #     await dev.async_turn_on(channel=0)
        # else:
        #     print(f"Turing off {dev.name}")
        #     await dev.async_turn_off(channel=0)

        for x in range(5):
            status, pid = getstatusoutput("fping -6 -I" + interface + " " + myIPV6)
            print("status:",pid)
            if "is alive" in pid:
            # We can now start playing with that
                print(f"Turning on {dev.name}...")
                await dev.async_turn_on(channel=0)
                break
            await asyncio.sleep(5)
           
        if x > 5:
            print(f"Turing off {dev.name}")
            await dev.async_turn_off(channel=0)
       

        print("status: ", status)

    # await asyncio.sleep(5)
    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()

if __name__ == '__main__':
    # On Windows + Python 3.8, you should uncomment the following
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()