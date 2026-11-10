
#!/usr/bin/env python3
"""Merge three XMLTV feeds into a compressed XMLTV file using Python stdlib."""

import gzip
import os
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

PUBLIC_URL = 'https://raw.githubusercontent.com/teleonline/listas/main/epg.xml.gz'

EPGSHARE_URL = 'https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz'

OUTPUT = Path('merged_epg.xml.gz')


def download(url, target):
    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'EPG-Merger/1.0',
            'Accept-Encoding': 'identity'
        }
    )
    with urllib.request.urlopen(request, timeout=120) as response, open(target, 'wb') as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)

    if os.path.getsize(target) == 0:
        raise ValueError('Downloaded EPG is empty')


def xml_stream(path):
    with open(path, 'rb') as probe:
        compressed = probe.read(2) == b'\x1f\x8b'

    opener = gzip.open if compressed else open

    with opener(path, 'rb') as handle:
        context = ET.iterparse(handle, events=('start', 'end'))
        _, root = next(context)

        if root.tag != 'tv':
            raise ValueError('Source is not XMLTV (<tv> root missing)')

        for event, element in context:
            if event == 'end' and element in root:
                if element.tag in ('channel', 'programme'):
                    yield element
                root.remove(element)


def main():
    private_url = os.environ.get('PRIVATE_EPG_URL', '').strip()

    if not private_url:
        sys.exit('Missing PRIVATE_EPG_URL GitHub Actions secret')

    with tempfile.TemporaryDirectory() as tmp:

        feeds = [
            Path(tmp) / 'public.epg',
            Path(tmp) / 'private.epg',
            Path(tmp) / 'epgshare.epg',
        ]

        urls = [
            PUBLIC_URL,
            private_url,
            EPGSHARE_URL,
        ]

        # Download all three sources before merging.
        for url, path in zip(urls, feeds):
            print(f'Downloading {path.name}...')
            download(url, path)

        merged = ET.Element(
            'tv',
            {'generator-info-name': 'GitHub Actions EPG Merger'}
        )

        channel_ids = set()
        programme_keys = set()
        channels = []
        programmes = []

        for source in feeds:
            count = 0

            print(f'Processing {source.name}...')

            for element in xml_stream(source):

                if element.tag == 'channel':
                    cid = element.get('id', '')

                    if not cid or cid in channel_ids:
                        continue

                    channel_ids.add(cid)
                    channels.append(element)

                else:
                    cid = element.get('channel', '')

                    if not cid:
                        continue

                    title = element.findtext('title', default='')

                    key = (
                        cid,
                        element.get('start', ''),
                        element.get('stop', ''),
                        title
                    )

                    if key in programme_keys:
                        continue

                    programme_keys.add(key)
                    programmes.append(element)

                count += 1

            if not count:
                raise ValueError(
                    f'No channel/programme entries in {source.name}'
                )

        for element in channels:
            merged.append(element)

        for element in programmes:
            merged.append(element)

        if not channels or not programmes:
            raise ValueError(
                'Merge has no channels or programmes; refusing to replace output'
            )

        temp_output = OUTPUT.with_suffix('.xml.gz.tmp')

        with open(temp_output, 'wb') as raw:
            with gzip.GzipFile(
                filename='',
                mode='wb',
                fileobj=raw,
                compresslevel=6,
                mtime=0
            ) as gz:
                ET.ElementTree(merged).write(
                    gz,
                    encoding='utf-8',
                    xml_declaration=True
                )

        temp_output.replace(OUTPUT)

        print(
            f'Created {OUTPUT}: '
            f'{len(channels)} channels, '
            f'{len(programmes)} programmes'
        )


if __name__ == '__main__':
    main()
