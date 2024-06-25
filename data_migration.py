import sys
import os


def main():

    if len(sys.argv) < 2:
        print("Choose a file with database to read!")
        sys.exit(1)

    file_to_read=sys.argv[1]

    if not os.path.isfile(file_to_read):
        print(f"File '{file_to_read}' does not exist.")
        sys.exit(1)

    f=open(file_to_read, "r", encoding="utf8")
    txt=f.read()
    txt=txt.replace("\n"," ")
    txt=txt.replace("`","")
    txt=" ".join(txt.split())
    f.close()

    file_to_write = os.getcwd()+"/devicemanager/fixtures/fixtures.yaml"
    f = open(file_to_write, "w", encoding="utf8")

    table_names_to_find=[
                         "grupy", 
                         "inv_budynki",
                         "inv_modele",
                         "inv_pokoje",
                         "inv_producenci",
                         "inv_typy_urz",
                         "inv_urzadzenia",
                         "pracownicy",
                         "stopnie"
                        ]

    app_model_names_for_tables={
                                "grupy": "auth.group",
                                "inv_budynki": "inventory.building",
                                "inv_modele": "inventory.devicemodel",
                                "inv_pokoje": "inventory.room",
                                "inv_producenci": "inventory.manufacturer",
                                "inv_typy_urz": "inventory.devicetype",
                                "inv_urzadzenia": "inventory.device",
                                "pracownicy": "users.user",
                                "stopnie": "users.displaynamedecorator"
                                }

    column_names_replacement_for_tables={
                                        "grupy": {"pl": "name"},
                                        "inv_budynki": {"nazwa": "name"},
                                        "inv_modele": {"id_typu": "device_type", "id_producenta": "manufacturer",
                                                    "nazwa": "name", "opis": "description"},
                                        "inv_pokoje": {"id_budynku": "building", "nazwa": "room_number",
                                                    "opis": "description"},
                                        "inv_producenci": {"nazwa": "name"},
                                        "inv_typy_urz": {"nazwa": "name", "short": "short_name"},
                                        "inv_urzadzenia":{"id_pokoju": "room","id_pracownika": "owner","id_modelu": "device_model",
                                                       "serial": "serial_number","nr_inw": "inventory_number"},
                                        "pracownicy": {"login": "username", "imie": "first_name", "nazwisko": "last_name", "pokoj": "room",
                                                    "tel": "telephone_number", "www": "website_url", "id_stopnia": "name_decoration"},
                                        "stopnie": {"pl": "decorator"}
                                        }

    columns_to_ignore_for_tables={
                              "grupy":["en"],
                              "inv_budynki": ["opis"],
                              "inv_modele": [],
                              "inv_pokoje": [],
                              "inv_producenci": [],
                              "inv_typy_urz": [],
                              "inv_urzadzenia": ["ostatnia_mod", "opis", "wypozyczony"],
                              "pracownicy": ["id_grupy", "sort_field", "zdjecie", "widocznosc", "id_zespolu", "passwd"],
                              "stopnie": "en"
                             }

    additional_lines_for_tables={
                             "grupy": "    permissions: []\n",
                             "inv_budynki": "    faculty: 1\n",
                             "inv_modele": "",
                             "inv_pokoje": "",
                             "inv_producenci": "    description: ''\n",
                             "inv_typy_urz": "",
                             "inv_urzadzenia": "",
                             "pracownicy":"    password: ''\n"
                                          "    last_login: null\n"
                                          "    is_superuser: false\n"
                                          "    is_staff: false\n"
                                          "    is_active: false\n"
                                          "    date_joined: 2024-06-05 00:00:00+00:00\n"
                                          "    user_preferences: {}\n"
                                          "    groups: []\n"
                                          "    user_permissions: []\n",
                             "stopnie": ""
                            }

    groups={"user": [], "group": []}


    for table_name in table_names_to_find:
        table_name_idx = txt.find("INSERT INTO " + table_name)
        column_names_start = txt.find("(", table_name_idx)+1
        column_names_end = txt.find(")", column_names_start)
        columns = txt[column_names_start:column_names_end]
        for key, value in column_names_replacement_for_tables[table_name].items():
            columns = columns.replace(key, value)
        columns = columns.split(", ")
    
        values_end = txt.find(";", column_names_end)
        row_end = txt.find("VALUES", column_names_start)
        rows=[]

        while(True):
            row_start = txt.find("(", row_end, values_end)+1
            row_end = txt.find("), (", row_start, values_end)
            if(row_start==0):
                break
            if(row_end==-1):
                row_end = txt.find(");", row_start, values_end+1)
            row = txt[row_start:row_end]
            row=row.replace(":","")
            row = row.split(", ")

            new_row=[]
            for i in range(len(row)):
                if(len(new_row)>0 and new_row[-1].count("'")%2==1):
                    new_row[-1]+=row[i]
                else:
                    new_row.append(row[i])
            
            row=new_row
            row = list(map(lambda item: item.replace("'","") , row))

            rows.append(row)

        for row_idx in range(len(rows)):
            f.write(f"- model: {app_model_names_for_tables[table_name]}\n")
            for i, column in enumerate(columns):
                if table_name=="pracownicy" and column=="id_grupy":
                    groups["group"].append(rows[row_idx][i])
                if column in columns_to_ignore_for_tables[table_name]:
                    continue
                if table_name=="pracownicy" and column == 'id':
                    groups["user"].append(rows[row_idx][i])
                if column == 'id':
                    f.write("  pk: " + rows[row_idx][i] + "\n")
                    f.write("  fields:\n")
                elif len(rows[row_idx][i])==0:
                    f.write(f"    {columns[i]}: ''\n")
                elif table_name=="inv_pokoje" and column=="room_number":
                    f.write(f"    {columns[i]}: '{rows[row_idx][i]}'\n")
                elif table_name=="inv_urzadzenia" and column.find("_number")!=-1 and rows[row_idx][i].isnumeric():
                    f.write(f"    {columns[i]}: '{rows[row_idx][i]}'\n")
                else:
                    f.write(f"    {columns[i]}: {rows[row_idx][i]}\n")
            f.write(additional_lines_for_tables[table_name])

    for i in range(len(groups["user"])):
        f.write("- model: users.user_groups\n")
        f.write(f"  pk: {i+1}\n")
        f.write("  fields:\n")
        f.write("    user: "+groups["user"][i]+"\n")
        f.write("    group: "+groups["group"][i]+"\n")

    f.write("- model: inventory.faculty\n")
    f.write("  pk: 1\n")
    f.write("  fields:\n")
    f.write("    full_name: Wydział Fizyki i Informatyki Stosowanej\n")
    f.write("    short_name: WFiIS\n")

    f.close()

if __name__ == "__main__":
    main()
