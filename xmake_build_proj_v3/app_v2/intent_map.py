from collections import defaultdict

intent_map_ext = {
    "Payment_Info": ["/sap/opu/odata/DHSPU/C_QR_FID_PAYMENT_CDS/xDHSPUxC_QR_FID_PAYMENT?$filter=({})&$format=json", None],
    "Pay_ID": ["/sap/opu/odata/DHSPU/C_QR_PAYID_DETAIL_CDS/xDHSPUxC_QR_PAYID_DETAIL?$filter=({})&$format=json", 
                "/sap/opu/odata/DHSPU/C_QR_PAYID_NSEARCH_CDS/xDHSPUxC_QR_PAYID_NSEARCH({})/Set/?$format=json"],
    "Bank_Info": ["/sap/opu/odata/DHSPU/C_QR_BANK_DETAIL_CDS/xDHSPUxC_QR_BANK_DETAIL?$filter=({})&$format=json", 
                "/sap/opu/odata/DHSPU/C_QR_BANK_NSEARCH_CDS/xDHSPUxC_QR_BANK_NSEARCH({})/Set/?$format=json"],
    "Lock_Validity": ["/sap/opu/odata/DHSPU/C_QR_PAY_DEST_LOCK_CDS/xDHSPUxC_QR_PAY_DEST_LOCK?$filter=({})&$format=json", None],
    "Payment_Details": ["/sap/opu/odata/DHSPU/C_QR_FID_PAYMENT_CDS/xDHSPUxC_QR_FID_PAYMENT?$filter=({})&$format=json", None],
    "Payment_Amount":["/sap/opu/odata/DHSPU/C_QR_FIDADDR_CDS/xDHSPUxC_QR_FIDADDR({})/Set/?$format=json", None],
    "Payment_Deduction": ["/sap/opu/odata/DHSPU/C_QR_DED_RT_CDS/xDHSPUxC_QR_DED_RT?$filter=(({}))&$format=json", None]
}

intent_map = {
    "Payment_Info": "/sap/opu/odata/DHSPU/C_QR_FID_PAYMENT_CDS/xDHSPUxC_QR_FID_PAYMENT?$filter=({})&$format=json",
    "Pay_ID": "/sap/opu/odata/DHSPU/C_QR_PAYID_DETAIL_CDS/xDHSPUxC_QR_PAYID_DETAIL?$filter=({})&$format=json",
    "Bank_Info": "/sap/opu/odata/DHSPU/C_QR_BANK_DETAIL_CDS/xDHSPUxC_QR_BANK_DETAIL?$filter=({})&$format=json",
    "Lock_Validity": "/sap/opu/odata/DHSPU/C_QR_PAY_DEST_LOCK_CDS/xDHSPUxC_QR_PAY_DEST_LOCK?$filter=({})&$format=json",
    "Payment_Details": "/sap/opu/odata/DHSPU/C_QR_FID_PAYMENT_CDS/xDHSPUxC_QR_FID_PAYMENT?$filter=({})&$format=json",
    "Payment_Amount":"/sap/opu/odata/DHSPU/C_QR_FIDADDR_CDS/xDHSPUxC_QR_FIDADDR({})/Set/?$format=json",
    "Payment_Deduction": "/sap/opu/odata/DHSPU/C_QR_DED_RT_CDS/xDHSPUxC_QR_DED_RT?$filter=(({}))&$format=json"
}

intent_field_map = {
    "Payment_Info": ("BPIdentificationNumber", "DATE", 'DATE_',"PaymentGroup", "Agency"),
    "Pay_ID": ("BPIdentificationNumber", "NAME"),
    "Bank_Info": ('BPIdentificationNumber', "NAME"),
    "Lock_Validity": ("BankAccountNumber", "BSBNumber", "ReasonText"),
    "Payment_Details": ("ExternalKey",),
    "Payment_Amount":("POSTCODE", "DATE", 'DATE_'),
    "Payment_Deduction": ("BPIdentificationNumber", "DATE", 'DATE_')
}

filter_separator_map = defaultdict(lambda: ' and ')
filter_separator_map['Payment_Amount'] = ','