from flask import Flask, request, Response
import contentful
from algoliasearch.search_client import SearchClient

app = Flask(__name__)


@app.route('/publish_entry', methods=['POST'])
def return_response():
    contentful_access = contentful.Client(
        'm1cn8nphj4ip',
        'HDyVTqB106kPDJnCxOyevs_bizDIz_zO98HiaqObR9A'
    )

    algolia_client = SearchClient.create(
        "7FY8RLNQEK", "47724aeef5a54f9e8718403e488601fe")

    index = algolia_client.init_index('test_index')

    re = request.json

    id = re["entityId"]
    product = contentful_access.entries(
        {
            'content_type': "product",
            'sys.id[match]': id
        }
    ).items[0].fields()

    # Product
    product_name = product["product_name"]
    price = product["price"]
    description = product["descriptions"]
    brand = product["brand"]

    record = {
        "objectID": id,
        "name": product_name,
        "price": price,
        "description": description,
        "brand": brand,
    }

    # Brand
    # brand_id = product["brand"].id
    # brand_entity = contentful_access.entries(
    #     {
    #         'content_type': "brand",
    #         'sys.id[match]': brand_id
    #     }
    # ).items[0].fields()

    # record["brand"] = brand_entity["name"]

    # Category
    category_ids = [x.id for x in product["categories"]]
    # record["category"] = []

    for cat_id in category_ids:
        cat = contentful_access.entries(
            {
                'content_type': "category",
                'sys.id[match]': cat_id
            }
        ).items[0].fields()

        # record["category"].append(cat["category_name"][0])
        record["category"] = cat["category_name"][0]

    # Specification
    specification_ids = [x.id for x in product["specifications"]]
    record["specification"] = {}

    for spec_id in specification_ids:
        spec = contentful_access.entries(
            {
                'content_type': "specification",
                'sys.id[match]': spec_id
            }
        ).items[0].fields()

        record["specification"][spec["specification_name"]] = spec["specification_value"]

    # images
    record["images"] = f'https://{product["image"][0].url().replace("//", "")}'

    # save to algolia
    index.save_object(record).wait()
    print("Algolia Updated")

    return Response(status=200)


if __name__ == "__main__":
    app.run(host="localhost", port=7071)