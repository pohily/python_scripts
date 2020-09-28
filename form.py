CODES = {
    1: 'адыг, майкоп',
    2: 'башкортостан, уфы, стерлитамак',
    3: 'бурят, улан',
    4: 'алтай, района ра',
    5: 'дагестан, кизилюрт, махачкал, хасавюрт',
    6: 'ингушет, малгобек',
    7: 'кабард, балкар, кбр, нальчик',
    8: 'калмык',
    9: 'карачаев, черкес',
    }
if __name__ == '__main__':
    with open('wrongFormFields.csv') as file:
        result = []
        for index, line in enumerate(file):
            if index:
                id, fid, vid, val, pid = line.split('::')
                if val == '(не выбрано)':
                    continue
                if vid[0].isdecimal():
                    code = int(vid[0])
                else:
                    result.append(line.replace('::', ';'))
                if not code:
                    result.append(line.replace('::', ';'))
                    continue

                ok = False
                terrs = CODES[code].split(',')
                for terr in terrs:
                    if terr in val.lower():
                        ok = True
                        break
                if not ok:
                    result.append(line.replace('::', ';'))
        with open('wrong_form_field.csv', 'w') as output:
            for line in result:
                output.write(line)
                print(line)
            print(len(result))
