from aws_config import get_dynamodb_resource, DYNAMODB_TABLE_NAME


def get_table():
    """Mengambil object table DynamoDB."""
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(DYNAMODB_TABLE_NAME)


def put_metadata(item):
    """Menyimpan metadata gambar."""
    table = get_table()
    table.put_item(Item=item)


def get_metadata(image_id):
    """Mengambil satu metadata berdasarkan image_id."""
    table = get_table()

    response = table.get_item(
        Key={"image_id": image_id}
    )

    return response.get("Item")


def list_metadata():
    """Mengambil seluruh metadata gambar."""
    table = get_table()

    items = []
    response = table.scan()
    items.extend(response.get("Items", []))

    # Scan DynamoDB dapat menghasilkan LastEvaluatedKey.
    # Loop ini membuat fungsi tetap mengambil seluruh data.
    while "LastEvaluatedKey" in response:
        response = table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response.get("Items", []))

    return items


def delete_metadata(image_id):
    """Menghapus metadata berdasarkan image_id."""
    table = get_table()

    table.delete_item(
        Key={"image_id": image_id}
    )
