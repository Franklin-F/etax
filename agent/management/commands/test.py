import django_subcommands
from .tests.test_queue import *
from .tests.test_service import *
from .tests.test_agent_login import *
from .tests.test_agent_getinvoice import *
from .tests.test_agent_getinvoicefile import *
from .tests.test_agent_filevat import *
from .tests.test_agent_getdeduction import *
from .tests.test_agent_getcurrentdeduction import *
from .tests.test_agent_revoketax import *
from .tests.test_agent_invoicing import *
from .tests.test_agent_invoicequota import *
from .tests.test_agent_filebsis import *
from .tests.test_agent_filecit import *
from .tests.test_stamp_duty import *


class Command(django_subcommands.SubCommands):
    subcommands = {
        "send-queue": SendQueue,
        "receive-queue": ReceiveQueue,
        "send-rabbitmq": SendRabbitmq,
        "receive-rabbitmq": ReceiveRabbitmq,
        "receive-service": ReceiveService,
        "sleep-service": SleepService,
        "bug-service": BugService,

        "create-login": CreateLogin,
        "create-getinvoicefile": CreateGetInvoiceFile,
        "create-getinvoice": CreateGetInvoice,
        "create-filevat": CreateFileVat,
        "create-getdeduction": CreateGetDeduction,
        "create-getcurrentdeduction": CreateGetCurrentDeduction,
        "create-revoketax": CreateRevokeTax,
        "create-invoicing": CreateInvoicing,
        "create-invoicequota": CreateInvoiceQuota,
        "create-filebsis": CreateFileBsis,
        "create-filecit": CreateFileCit,
        "create-stampduty": CreateStampDuty,
    }
