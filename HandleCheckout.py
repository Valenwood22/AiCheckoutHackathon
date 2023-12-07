import csv


def handle_checkout(array):
    result = {
        'grand_total': 0.00,
        'itemsPurchased': []
    }

    with open('inventory.csv', mode='r') as file:
        csv_file = csv.reader(file)
        for lines in csv_file:
            code = lines[0]
            item = lines[1].strip()
            price = lines[2]
            cart = {
                "barcode": code,
                "item": item,
                "price": price,
                "qty": 0,
                "total": 0.00
            }
            for barcode in array:
                if barcode == lines[0]:
                    cart['total'] = cart['total'] + float(lines[2])
                    cart['qty'] += 1

            if cart['total'] > 0.00:
                result['itemsPurchased'].append(cart)

    for item in result['itemsPurchased']:
        result['grand_total'] = round(float(result['grand_total']) + float(item['total']), 2)

    return result

# To test the function uncomment this line
# print(handle_checkout(['099482458522', '029059592049', '099482458522']))
