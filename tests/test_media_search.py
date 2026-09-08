import base64
import struct

from tests.conftest import add_media


def _emb(values):
    packed = b"".join(struct.pack("<f", float(v)) for v in values)
    return base64.b64encode(packed).decode("ascii")


def test_unindexed_returns_new_images_not_failed_out(client, db, device_a, headers_a):
    fresh = add_media(db, device_a, file_name="new.jpg")
    exhausted = add_media(db, device_a, file_name="bad.jpg")
    exhausted.index_attempts = 3
    db.commit()

    r = client.get("/api/v1/media/unindexed?limit=20", headers=headers_a)
    assert r.status_code == 200
    ids = [m["id"] for m in r.json()]
    assert fresh.id in ids
    assert exhausted.id not in ids


def test_unindexed_does_not_leak_other_parent(client, db, device_a, device_b, headers_a):
    mine = add_media(db, device_a, file_name="mine.jpg")
    add_media(db, device_b, file_name="theirs.jpg")

    r = client.get("/api/v1/media/unindexed", headers=headers_a)
    assert r.status_code == 200
    ids = [m["id"] for m in r.json()]
    assert ids == [mine.id]


def test_search_finds_english_and_arabic_tags(client, db, device_a, headers_a):
    photo = add_media(db, device_a, file_name="cake.jpg")
    r = client.post(
        f"/api/v1/media/{photo.id}/index",
        headers=headers_a,
        json={
            "caption_en": "a boy with a cake",
            "caption_ar": "كيك",
            "tags": [{"tag_en": "cake", "tag_ar": "كيك", "score": 0.9}],
            "faces": [],
        },
    )
    assert r.status_code == 200

    en = client.get(f"/api/v1/devices/{device_a.id}/media/search?q=cake", headers=headers_a)
    ar = client.get(f"/api/v1/devices/{device_a.id}/media/search?q=كيك", headers=headers_a)
    assert en.status_code == 200
    assert ar.status_code == 200
    assert photo.id in [m["id"] for m in en.json()]
    assert photo.id in [m["id"] for m in ar.json()]


def test_unindexed_photo_is_in_gallery_not_in_keyword_search(client, db, device_a, headers_a):
    photo = add_media(db, device_a, file_name="raw.jpg")

    gallery = client.get(f"/api/v1/devices/{device_a.id}/media/", headers=headers_a)
    search = client.get(f"/api/v1/devices/{device_a.id}/media/search?q=cake", headers=headers_a)
    assert photo.id in [m["id"] for m in gallery.json()]
    assert search.json() == []


def test_parent_cannot_index_someone_elses_photo(client, db, device_b, headers_a):
    photo = add_media(db, device_b, file_name="secret.jpg")
    r = client.post(
        f"/api/v1/media/{photo.id}/index",
        headers=headers_a,
        json={"caption_en": "x", "caption_ar": "", "tags": [], "faces": []},
    )
    assert r.status_code == 403


def test_index_error_increments_attempts(client, db, device_a, headers_a):
    photo = add_media(db, device_a, file_name="corrupt.jpg")
    r = client.post(
        f"/api/v1/media/{photo.id}/index",
        headers=headers_a,
        json={"error": "unreadable image"},
    )
    assert r.status_code == 200
    db.refresh(photo)
    assert photo.indexed_at is None
    assert photo.index_attempts == 1
    assert photo.index_error == "unreadable image"


def test_naming_a_person_makes_name_searchable(client, db, device_a, headers_a):
    photo = add_media(db, device_a, file_name="face.jpg")
    r = client.post(
        f"/api/v1/media/{photo.id}/index",
        headers=headers_a,
        json={
            "caption_en": "",
            "caption_ar": "",
            "tags": [],
            "faces": [
                {
                    "bbox_x": 1,
                    "bbox_y": 2,
                    "bbox_w": 10,
                    "bbox_h": 10,
                    "embedding_b64": _emb([1, 0, 0, 0]),
                    "quality": 0.8,
                    "cluster_key": "p1",
                }
            ],
        },
    )
    assert r.status_code == 200
    people = client.get(f"/api/v1/devices/{device_a.id}/people", headers=headers_a)
    assert people.status_code == 200
    assert len(people.json()) == 1
    person_id = people.json()[0]["id"]
    assert people.json()[0]["name"] is None

    named = client.patch(
        f"/api/v1/devices/{device_a.id}/people/{person_id}",
        headers=headers_a,
        json={"name": "Ahmed"},
    )
    assert named.status_code == 200

    found = client.get(
        f"/api/v1/devices/{device_a.id}/media/search?q=Ahmed",
        headers=headers_a,
    )
    assert photo.id in [m["id"] for m in found.json()]

    by_person = client.get(
        f"/api/v1/devices/{device_a.id}/media/search?person_id={person_id}",
        headers=headers_a,
    )
    assert photo.id in [m["id"] for m in by_person.json()]


def test_embeddings_endpoint_returns_existing_faces(client, db, device_a, headers_a):
    photo = add_media(db, device_a, file_name="emb.jpg")
    client.post(
        f"/api/v1/media/{photo.id}/index",
        headers=headers_a,
        json={
            "caption_en": "",
            "caption_ar": "",
            "tags": [],
            "faces": [
                {
                    "bbox_x": 0,
                    "bbox_y": 0,
                    "bbox_w": 8,
                    "bbox_h": 8,
                    "embedding_b64": _emb([0, 1, 0, 0]),
                    "quality": 0.7,
                    "cluster_key": "x",
                }
            ],
        },
    )
    r = client.get(f"/api/v1/devices/{device_a.id}/people/embeddings", headers=headers_a)
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["person_id"] is not None
    assert body[0]["embedding_b64"]
