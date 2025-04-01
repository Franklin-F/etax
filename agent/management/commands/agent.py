import django_subcommands
from .agents.agent_login import LoginService
from .agents.agent_get_invoice import GetInvoiceService
from .agents.agent_download_invoice import DownloadInvoiceService
from .agents.agent_get_invoice_file import GetInvoiceFileService
from .agents.agent_get_deduction import GetDeductionService
from .agents.agent_get_current_deduction import GetCurrentDeductionService
from .agents.agent_file_vat import FileVatService
from .agents.agent_revoke_tax import RevokeTaxService
from .agents.agent_invoicing import InvoicingService
from .agents.agent_get_invoice_quota import InvoiceQuotaService
from .agents.agent_file_bsis import FileBsisService
from .agents.agent_file_cit import FileCitService
from .agents.agent_stamp_duty import StampDutyService


class Command(django_subcommands.SubCommands):
    subcommands = {
        "login": LoginService,
        "getinvoice": GetInvoiceService,
        "downloadinvoice": DownloadInvoiceService,
        "getinvoicefile": GetInvoiceFileService,
        "getdeduction": GetDeductionService,
        "getcurrentdeduction": GetCurrentDeductionService,
        "filevat": FileVatService,
        "revoketax": RevokeTaxService,
        "invoicing": InvoicingService,
        "invoicequota": InvoiceQuotaService,
        "filebsis": FileBsisService,
        "filecit": FileCitService,
        "stampduty": StampDutyService,
    }
