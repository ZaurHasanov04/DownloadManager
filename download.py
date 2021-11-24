import asyncio
import aiohttp
import aiofiles
import time
async def do(data: dict, session: aiohttp.ClientSession, tasks: list):
    response = await get_new_request(method="HEAD", url=data['Url'], session=session)
    # print(response.headers.items())
    size = response.headers.get('content-length')
    sections = [[0, 0] for _ in range(data['TotalSections'])]
    # print(data)
    each_size = int(size) // data['TotalSections']
    for index, _ in enumerate(sections):
        # print(index)
        if index == 0:
            sections[index][0] = 0
        else:
            sections[index][0] = sections[index - 1][1] + 1
        if index < data['TotalSections'] - 1:
            sections[index][1] = sections[index][0] + each_size
        else:
            sections[index][1] = int(size) - 1

    for index, section in enumerate(sections):
        
        tasks.append(asyncio.create_task(download_section(index, section, data, session)))
    return sections, tasks


async def get_new_request(method: str, url: str,
                          session: aiohttp.ClientSession, headers: dict = None) -> aiohttp.ClientResponse:
    if headers:
        headers['User-Agent'] = "Download Manager v001"
    return await session.request(method=method, url=url, headers=headers)


async def download_section(index: int, section: list,
                           data: dict, session: aiohttp.ClientSession):
    print(section)
    headers = {'Range': f"bytes={section[0]}-{section[1]}"} #f"bytes ne mena verir burda?
    print(headers)
    resp = await get_new_request(method="GET", url=data['Url'],session=session, headers=headers)
    file_name = f"section-{index}.tmp"
    data = await resp.content.read()
    f = await aiofiles.open(file_name, 'wb')
    await f.write(data)
    await f.close()


def merge_files(target_path: str, sections: list) -> None:
    with open(target_path, 'wb+') as final_file:
        for index, section in enumerate(sections):
            file_name = f"section-{index}.tmp"
            with open(file_name, 'rb') as section_file:
                final_file.write(section_file.read())
                

async def main(data: dict, tasks: list):
    async with aiohttp.ClientSession() as session:
        sections, tasks_ = await do(data=data, session=session, tasks=tasks)
        
        await asyncio.wait(tasks_)
    return sections

if __name__ == "__main__":
    d = {'Url': "https:...",
         'TargetPath': "5MB.zip",
         'TotalSections': 10}
    tasks = []
    sections = asyncio.run(main(data=d, tasks=tasks))
    
    merge_files(d['TargetPath'], sections=sections)
