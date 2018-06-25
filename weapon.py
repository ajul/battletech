import json
import os

data_path = (
    'C:/Program Files (x86)/Steam/steamapps/common/' +
    'BATTLETECH/BattleTech_Data/StreamingAssets/data'
    )

weapon_path = os.path.join(data_path, 'weapon')

# WeaponSubType -> stock data
stock_weapons = {}

def make_cost_string(data):
    cost = data['Description']['Cost'] // 1000
    if data['Description']['Purchasable']:
        return '<span style="color: white;">%d</span>' % cost
    else:
        return '<span style="color: gray;">%d</span>' % cost

def make_damage_string(data, key):
    damage_per_shot = data[key]
    stock_damage_per_shot = stock_weapons[data['WeaponSubType']][key]
    bonus_per_shot = damage_per_shot - stock_damage_per_shot
    
    shots = data['ShotsWhenFired']
    total_damage = damage_per_shot * shots
    is_multi = shots > 1 and damage_per_shot > 0

    data_sort_value = 'data-sort-value="%d" | ' % total_damage
    cell = '%d' % (total_damage)
    
    if is_multi:
        if bonus_per_shot > 0:
            cell += ' (%d+%d × %d)' % (stock_damage_per_shot, bonus_per_shot, shots)
        else:
            cell += ' (%d × %d)' % (damage_per_shot, shots)
    elif bonus_per_shot > 0:
        cell += ' (+%d)' % bonus_per_shot
        
    if bonus_per_shot > 0:
        cell = '<span style="color: palegreen;">%s</span>'% cell
    return data_sort_value + cell

def make_range_string(data):
    data_sort_value = '%d' % data['MaxRange']
    result = 'data-sort-value="%s" | %d / %d / %d' % (data_sort_value, data['MinRange'], data['RangeSplit'][1], data['MaxRange'],)

    return result

def make_other_string(data):
    other = []

    def append_other_item(key, format_string,
                          transform = lambda x: x,
                          default_raw = 0,
                          bonus_format = '(%+d)'):
        if data[key] == default_raw: return
        stock_raw = stock_weapons[data['WeaponSubType']][key]

        value = transform(data[key])
        stock_value = transform(stock_raw)
        bonus = value - stock_value
            
        item = format_string % value
        if bonus != 0:
            if stock_raw != default_raw:
                item += ' ' + (bonus_format % bonus)
            item = '<span style="color: palegreen;">%s</span>'% (item)
        other.append(item)

    if data['IndirectFireCapable']:
        other.append('Indirect fire')

    append_other_item('HeatDamage', '%d heat damage')

    if len(data['statusEffects']) > 0:
        other.append('Inflicts -1 accuracy debuff')
    
    if data['RefireModifier']:
        other.append('%d refire accuracy' % -data['RefireModifier'])

    append_other_item('AccuracyModifier', '%+d accuracy',
                      transform = lambda x: -x)

    append_other_item('CriticalChanceMultiplier', '%+d%% critical',
                      transform = lambda x: (x - 1.0) * 100,
                      default_raw = 1.0,
                      bonus_format = '(+%d%%)')

    return '<br/>'.join(other)

def make_row(data):
    row = [
        data['Description']['Name'].replace('+ ', '+'),
        data['Description']['Manufacturer'],
        data['Category'].replace('AntiPersonnel', 'Support'),
        make_cost_string(data),
        data['Tonnage'],
        data['InventorySize'],
        make_damage_string(data, 'Damage'),
        make_damage_string(data, 'Instability'),
        data['HeatGenerated'],
        make_range_string(data),
        make_other_string(data),
    ]

    return row

result = '{|class = "wikitable sortable"\n'
result += '! '

headers = [
    'Weapon',
    'Manufacturer',
    'Category',
    'Cost (k)',
    'Tonnage',
    'Slots',
    'Damage',
    'Stability<br/>damage',
    'Heat',
    'Range (m)<br/>min/opt/max',
    'Other',
    ]

result += ' !! '.join(headers)

result += '\n'

rows = []

for filename in os.listdir(weapon_path):
    if filename == 'WeaponTemplate.json': continue
    path = os.path.join(weapon_path, filename)
    f = open(path)
    data = json.load(f)
    f.close()

    if 'STOCK' in filename: stock_weapons[data['WeaponSubType']] = data
    
    if data['Category'] == "Melee": continue
    if data['WeaponSubType'] == 'AIImaginary': continue
    
    rows.append((data, make_row(data)))

def sort_func(data):
    name = data['Description']['Name']

    if 'AC/' in name:
        magic = ('AC', data['Tonnage'])
    elif 'Laser' in name or 'Pulse' in name:
        magic = ('Laser', data['Tonnage'])
    elif 'PPC' in name:
        magic = ('PPC', data['HeatGenerated'])
    elif 'RM' in name:
        magic = (name[:3], data['Tonnage'])
    else:
        magic = (name,)
        
    
    return (
        data['Category'].replace('AntiPersonnel', 'Support'),
        not data['Description']['Purchasable'],
        magic,
        data['Description']['Name'].replace('+ ', '+'),
        data['Description']['Manufacturer'],
        )

rows.sort(key = lambda x: sort_func(x[0]))

for _, row in rows:
    result += '|-\n'
    result += '| '
    result += ' || '.join(str(x) for x in row)
    result += '\n'

result += '|}\n'

print(result)
