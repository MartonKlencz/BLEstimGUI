from bleak import BleakClient

async def connectBLE(address, serv_UUID, char_UUID):
    client = BleakClient(address)
    service = None
    characteristic = None
    try:
        await client.connect()
        service = client.services.get_service(serv_UUID)
        characteristic = service.get_characteristic(char_UUID)
    except:
        print("Connection error")

    return client, service, characteristic

async def sendBLE(client, data, UUID):

    await client.write_gatt_char(UUID, data, response=False)

#
# client = asyncio.run(connectBLE(address))
# data = bytearray([0x69, 0x01, 0x0, 0x0, 0x0, 0x0, 0x0, 0x6a])
#
# for i in range(10):
#     asyncio.run(sendBLE(client, data))

