"""Seed script: add Angel Company HospitalAngel as a mock client."""

import asyncio

import httpx

CRM_BASE = "http://127.0.0.1:8000/api/v1"


async def main() -> None:
    async with httpx.AsyncClient(base_url=CRM_BASE) as client:
        # Step 1: Trigger dev user bootstrap by hitting contacts list
        print("Bootstrapping dev user...")
        r = await client.get("/contacts/")
        print(f"  Bootstrap: {r.status_code}")
        if r.status_code >= 400:
            print(f"  Response: {r.text}")
            return

        # Step 2: Create a promoter
        print("Creating promoter 'Default Promoter'...")
        r = await client.post(
            "/contacts/promoters",
            json={"name": "Default Promoter", "phone": "+52 81 0000 0000"},
        )
        print(f"  Promoter create: {r.status_code}")
        if r.status_code >= 400:
            print(f"  Response: {r.text}")
            return
        promoter = r.json()
        promoter_id = promoter["id"]
        print(f"  Promoter ID: {promoter_id}")

        # Step 3: Create the company contact
        print("Creating company 'Angel Company HospitalAngel'...")
        r = await client.post(
            "/contacts/",
            json={
                "type": "COMPANY",
                "name": "Angel Company HospitalAngel",
                "promoter_id": promoter_id,
                "industry": "Hospital",
                "company_people": [
                    {
                        "name": "Contact Person",
                        "phone": "+52 81 1111 1111",
                        "email": "contact@angelhospital.com",
                        "position": "Director",
                    }
                ],
            },
        )
        print(f"  Contact create: {r.status_code}")
        if r.status_code >= 400:
            print(f"  Response: {r.text}")
            return
        contact = r.json()
        print(f"  Contact ID: {contact['id']}")
        print(f"  Name: {contact['name']}")
        print(f"  Industry: {contact['industry']}")
        print("Done! Mock client created successfully.")


if __name__ == "__main__":
    asyncio.run(main())
