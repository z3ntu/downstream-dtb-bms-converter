#!/usr/bin/env python3
import struct
import sys

import libfdt


def find_subnode_by_name(fdt, node, name):
    for subnode in fdt_for_each_subnode(fdt, node):
        if fdt.get_name(subnode) == name:
            return subnode


def fdt_as_array(self, fmt):
    unpack_iter = struct.iter_unpack('>' + fmt, self)
    ret = []
    for val in unpack_iter:
        ret.append(val[0])
    return ret


def fdt_as_int32_array(self):
    return fdt_as_array(self, 'l')


def fdt_for_each_subnode(fdt, nodeoffset):
    subnode_offset = fdt.first_subnode(nodeoffset)
    yield subnode_offset
    while True:
        try:
            subnode_offset = fdt.next_subnode(subnode_offset)
            yield subnode_offset
        except libfdt.FdtException:
            return


def print_for_bms_old(fcc_lut_col_legend, fcc_lut_data, ocv_lut_row_legend, ocv_lut_col_legend, ocv_lut_data):
    fcc_temp_legend = ["{0}{2:d}{1}".format('(' if x < 0 else '', ')' if x < 0 else '', x) for x in
                       fcc_lut_col_legend]
    fcc_temp_legend = " ".join(fcc_temp_legend)

    fcc_lut = [str(n) for n in fcc_lut_data]
    fcc_lut = " ".join(fcc_lut)

    ocv_capacity_legend = [str(n) for n in ocv_lut_row_legend]
    ocv_capacity_legend = " ".join(ocv_capacity_legend)

    ocv_temp_legend = ["{0}{2:d}{1}".format('(' if x < 0 else '', ')' if x < 0 else '', x) for x in
                       ocv_lut_col_legend]
    ocv_temp_legend = " ".join(ocv_temp_legend)

    ocv_lut = [str(n) for n in ocv_lut_data]
    ocv_lut = " ".join(ocv_lut)

    print("\tqcom,fcc-temp-legend = /bits/ 8 <{}>;".format(fcc_temp_legend))
    print("\tqcom,fcc-lut = /bits/ 16 <{}>;".format(fcc_lut))
    print()
    print("\tqcom,ocv-capacity-legend = /bits/ 8 <{}>;".format(ocv_capacity_legend))
    print("\tqcom,ocv-temp-legend = /bits/ 8 <{}>;".format(ocv_temp_legend))
    print("\tqcom,ocv-lut = /bits/ 16 <{}>;".format(ocv_lut))


def print_for_bms_current(fcc_lut_col_legend, fcc_lut_data, ocv_lut_row_legend, ocv_lut_col_legend, ocv_lut_data):
    fcc_temp_legend = ["{0}{2:d}{1}".format('(' if x < 0 else '', ')' if x < 0 else '', x) for x in
                       fcc_lut_col_legend]
    fcc_temp_legend = " ".join(fcc_temp_legend)

    fcc_lut = [str(n * 1000) for n in fcc_lut_data]
    fcc_lut = " ".join(fcc_lut)

    ocv_capacity_legend = [str(n) for n in ocv_lut_row_legend]
    ocv_capacity_legend = " ".join(ocv_capacity_legend)

    ocv_temp_legend = ["{0}{2:d}{1}".format('(' if x < 0 else '', ')' if x < 0 else '', x) for x in
                       ocv_lut_col_legend]
    ocv_temp_legend = " ".join(ocv_temp_legend)

    ocv_lut = [str(n * 1000) for n in ocv_lut_data]
    ocv_lut = " ".join(ocv_lut)

    print("\tqcom,fcc-temp-legend-celsius = /bits/ 8 <{}>;".format(fcc_temp_legend))
    print("\tqcom,fcc-lut-microamp-hours = <{}>;".format(fcc_lut))
    print()
    print("\tqcom,ocv-capacity-legend = /bits/ 8 <{}>;".format(ocv_capacity_legend))
    print("\tqcom,ocv-temp-legend-celsius = /bits/ 8 <{}>;".format(ocv_temp_legend))
    print("\tqcom,ocv-lut-microvolt = <{}>;".format(ocv_lut))


def print_for_bms_next(fcc_lut_col_legend, fcc_lut_data, ocv_lut_row_legend, ocv_lut_col_legend, ocv_lut_data):
    ocv_temperatures = ["{0}{2:d}{1}".format('(' if x < 0 else '', ')' if x < 0 else '', x) for x in
                        ocv_lut_col_legend]
    ocv_temperatures = " ".join(ocv_temperatures)

    print("\tocv-capacity-celsius = <{}>;".format(ocv_temperatures))

    for index, temp in enumerate(ocv_lut_col_legend):
        print("\tocv-capacity-table-{} = ".format(index), end='')
        for index_cap, capacity in enumerate(ocv_lut_row_legend):
            # Get the correct data element
            volt = ocv_lut_data[index_cap * len(ocv_lut_col_legend) + index] * 1000
            if index_cap > 0:
                print(", ", end='')
                # Print newline after four elements
                if (index_cap - 4) % 4 == 0:
                    print('')
                    print('\t\t\t       ', end='')
            print("<{} {}>".format(volt, capacity), end='')
        print(';')

    # TODO Handle fcc_lut_col_legend , fcc_lut_data , temp


def main():
    if len(sys.argv) < 2:
        print("Usage: {} <dtb_file>".format(sys.argv[0]))
        sys.exit(1)

    with open(sys.argv[1], mode='rb') as f:
        fdt = libfdt.FdtRo(f.read())

    batterydata = fdt.path_offset('/qcom,battery-data')

    for battery_subnode in fdt_for_each_subnode(fdt, batterydata):
        name = fdt.get_name(battery_subnode)
        print(name)
        fcc_temp_lut = find_subnode_by_name(fdt, battery_subnode, "qcom,fcc-temp-lut")

        fcc_lut_col_legend = fdt.getprop(fcc_temp_lut, "qcom,lut-col-legend")
        fcc_lut_data = fdt.getprop(fcc_temp_lut, "qcom,lut-data")

        fcc_lut_col_legend = fdt_as_int32_array(fcc_lut_col_legend)
        fcc_lut_data = fdt_as_int32_array(fcc_lut_data)
        # print(fcc_lut_col_legend)
        # print(fcc_lut_data)

        pc_temp_ocv_lut = find_subnode_by_name(fdt, battery_subnode, "qcom,pc-temp-ocv-lut")
        ocv_lut_col_legend = fdt.getprop(pc_temp_ocv_lut, "qcom,lut-col-legend")
        ocv_lut_row_legend = fdt.getprop(pc_temp_ocv_lut, "qcom,lut-row-legend")
        ocv_lut_data = fdt.getprop(pc_temp_ocv_lut, "qcom,lut-data")

        ocv_lut_col_legend = fdt_as_int32_array(ocv_lut_col_legend)
        ocv_lut_row_legend = fdt_as_int32_array(ocv_lut_row_legend)
        ocv_lut_data = fdt_as_int32_array(ocv_lut_data)

        # print(ocv_lut_col_legend)
        # print(ocv_lut_row_legend)
        # print(ocv_lut_data)

        print("bms@4000 {")
        print("\tstatus = \"okay\";")

        print("\n\t/* bms old */")
        print_for_bms_old(fcc_lut_col_legend, fcc_lut_data, ocv_lut_row_legend, ocv_lut_col_legend, ocv_lut_data)
        print("\n\t/* bms current */")
        print_for_bms_current(fcc_lut_col_legend, fcc_lut_data, ocv_lut_row_legend, ocv_lut_col_legend, ocv_lut_data)
        print("\n\t/* bms next */")
        print_for_bms_next(fcc_lut_col_legend, fcc_lut_data, ocv_lut_row_legend, ocv_lut_col_legend, ocv_lut_data)

        print("};")

        # sw = libfdt.FdtSw()
        # sw.finish_reservemap()
        # with sw.add_node(''):
        #     with sw.add_node('bms@4000'):
        #         sw.property_string('status', 'okay')
        #         sw.property_u64('test', 0xFFFFFFFFFFFFFFF)
        # fdt_new = sw.as_fdt()
        #
        # bytearr = fdt_new.as_bytearray()
        # with open(name + '.dtb', 'wb') as f:
        #     f.write(bytearr)

        # Now we can use it as a real device tree
        # fdt.setprop_u32(0, 'reg', 3)


if __name__ == '__main__':
    main()
