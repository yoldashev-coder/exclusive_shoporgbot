import asyncio
import aiohttp
from services.api_service import DummyJSONService

async def main():
    service = DummyJSONService()
    print(f"Testing API URL: {service.base_url}/products/categories")
    
    try:
        categories = await service.get_categories()
        print(f"Status: Success")
        print(f"Count: {len(categories)}")
        if categories:
            print(f"First item: {categories[0]}")
            print(f"Type of first item: {type(categories[0])}")
        else:
            print("Categories list is empty!")
            
    except Exception as e:
        print(f"Status: Failed")
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
