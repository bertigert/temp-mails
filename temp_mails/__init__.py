import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .providers.adguard_com import Adguard_com
    from .providers.anonymmail_net import Anonymmail_net        
    from .providers.burnermailbox_com import Burnermailbox_com  
    from .providers.byom_de import Byom_de
    from .providers.cloudtempmail_com import Cloudtempmail_com  
    from .providers.correotemporal_org import Correotemporal_org
    from .providers.crazymailing_com import Crazymailing_com    
    from .providers.cryptogmail_com import Cryptogmail_com      
    from .providers.disposableemail_co import Disposableemail_co
    from .providers.disposablemail_com import Disposablemail_com
    from .providers.dropmail_me import Dropmail_me
    from .providers.emaildashfake_com import Emaildashfake_com
    from .providers.emaildashfree_online import Emaildashfree_online
    from .providers.emailfake_com import Emailfake_com
    from .providers.emailondeck_com import Emailondeck_com
    from .providers.emailtenmin_com import Emailtenmin_com
    from .providers.etempmail_com import Etempmail_com
    from .providers.etempmail_net import Etempmail_net
    from .providers.expressinboxhub_com import Expressinboxhub_com
    from .providers.eyepaste_com import Eyepaste_com
    from .providers.eztempmail_com import Eztempmail_com
    from .providers.fakemail_net import Fakemail_net
    from .providers.fakemailgenerator_com import Fakemailgenerator_com
    from .providers.fakermail_com import Fakermail_com
    from .providers.fmail_sbs import Fmail_sbs
    from .providers.fumail_co import Fumail_co
    from .providers.generator_email import Generator_email
    from .providers.getnada_cc import Getnada_cc
    from .providers.gmailcity_com import Gmailcity_com
    from .providers.guerillamail_com import Guerillamail_com
    from .providers.harakirimail_com import Harakirimail_com
    from .providers.haribu_net import Haribu_net
    from .providers.inboxes_com import Inboxes_com
    from .providers.inboxkitten_com import Inboxkitten_com
    from .providers.incognitomail_co import Incognitomail_co
    from .providers.internxt_com import Internxt_com
    from .providers.lroid_com import Lroid_com
    from .providers.luxusmail_org import Luxusmail_org
    from .providers.maidashtemp_com import Maidashtemp_com
    from .providers.mail_gw import Mail_gw
    from .providers.mail_td import Mail_td
    from .providers.mail_tm import Mail_tm
    from .providers.mailcatch_com import Mailcatch_com
    from .providers.maildax_com import Maildax_com
    from .providers.mailforspam_com import Mailforspam_com
    from .providers.mailfourqa_com import Mailfourqa_com
    from .providers.mailgolem_com import Mailgolem_com
    from .providers.mailhole_de import Mailhole_de
    from .providers.mailinator_com import Mailinator_com
    from .providers.maillog_org import Maillog_org
    from .providers.mailnesia_com import Mailnesia_com
    from .providers.mailper_com import Mailper_com
    from .providers.mailsac_com import Mailsac_com
    from .providers.mailseven_io import Mailseven_io
    from .providers.mailtemp_net import Mailtemp_net
    from .providers.mailtemp_uk import Mailtemp_uk
    from .providers.mintemail_com import Mintemail_com
    from .providers.minuteinbox_com import Minuteinbox_com
    from .providers.minutemailbox_com import Minutemailbox_com
    from .providers.moakt_com import Moakt_com
    from .providers.mohmal_com import Mohmal_com, Mohamal_com
    from .providers.mostakbile_com import Mostakbile_com
    from .providers.muellmail_com import Muellmail_com
    from .providers.nicemail_cc import Nicemail_cc
    from .providers.noopmail_org import Noopmail_org
    from .providers.onesecmail_com import Onesecmail_com
    from .providers.priyo_email import Priyo_email
    from .providers.rainmail_xyz import Rainmail_xyz
    from .providers.schutzdashmail_de import Schutzdashmail_de
    from .providers.segamail_com import Segamail_com
    from .providers.temils_com import Temils_com
    from .providers.tempail_com import Tempail_com
    from .providers.tempdashemail_info import Tempdashemail_info
    from .providers.tempdashinbox_com import Tempdashinbox_com
    from .providers.tempdashinbox_me import Tempdashinbox_me
    from .providers.tempdashmail_gg import Tempdashmail_gg
    from .providers.tempdashmail_id import Tempdashmail_id
    from .providers.tempdashmail_io import Tempdashmail_io
    from .providers.tempdashmail_org import Tempdashmail_org
    from .providers.tempdashmailbox_net import Tempdashmailbox_net
    from .providers.tempemail_co import Tempemail_co
    from .providers.tempemailfree_com import Tempemailfree_com
    from .providers.tempemailgen_com import Tempemailgen_com
    from .providers.tempinbox_xyz import Tempinbox_xyz
    from .providers.tempm_com import Tempm_com
    from .providers.tempmail_cc import Tempmail_cc
    from .providers.tempmail_email import Tempmail_email
    from .providers.tempmail_gg import Tempmail_gg
    from .providers.tempmail_guru import Tempmail_guru
    from .providers.tempmail_lol import Tempmail_lol
    from .providers.tempmail_net import Tempmail_net
    from .providers.tempmail_ninja import Tempmail_ninja
    from .providers.tempmail_plus import Tempmail_plus
    from .providers.tempmailbeast_com import Tempmailbeast_com
    from .providers.tempmailbox_net import Tempmailbox_net
    from .providers.tempmailer_net import Tempmailer_net
    from .providers.tempmailers_com import Tempmailers_com
    from .providers.tempmailinbox_com import Tempmailinbox_com
    from .providers.tempmails_net import Tempmails_net
    from .providers.tempmailso_com import Tempmailso_com
    from .providers.tempomail_com import Tempomail_com
    from .providers.tempomail_top import Tempomail_top
    from .providers.temporarymail_com import Temporarymail_com
    from .providers.temppdashmails_com import Temppdashmails_com
    from .providers.tempr_email import Tempr_email
    from .providers.tendashminutemail_net import Tendashminutemail_net
    from .providers.tenminemail_com import Tenminemail_com
    from .providers.tenminuteemail_com import Tenminuteemail_com
    from .providers.tenminuteemails_com import Tenminuteemails_com
    from .providers.tenminutemail_one import Tenminutemail_one
    from .providers.tenminutesemail_net import Tenminutesemail_net
    from .providers.tmail_ai import Tmail_ai
    from .providers.tmail_gg import Tmail_gg
    from .providers.tmail_io import Tmail_io
    from .providers.tmailor_com import Tmailor_com
    from .providers.tmdashmail_com import Tmdashmail_com
    from .providers.tmpmail_co import Tmpmail_co
    from .providers.trashmail_com import Trashmail_com
    from .providers.trashmail_de import Trashmail_de
    from .providers.trashmail_ws import Trashmail_ws
    from .providers.treemail_pro import Treemail_pro
    from .providers.txen_de import Txen_de
    from .providers.upxmail_com import Upxmail_com
    from .providers.wpdashtempmail_com import Wpdashtempmail_com
    from .providers.yopmail_com import Yopmail_com
    from .providers.zemail_me import Zemail_me

_provider_map = {
     "Adguard_com": "adguard_com",
    "Anonymmail_net": "anonymmail_net",
    "Burnermailbox_com": "burnermailbox_com",
    "Byom_de": "byom_de",
    "Cloudtempmail_com": "cloudtempmail_com",
    "Correotemporal_org": "correotemporal_org",
    "Crazymailing_com": "crazymailing_com",
    "Cryptogmail_com": "cryptogmail_com",
    "Disposableemail_co": "disposableemail_co",
    "Disposablemail_com": "disposablemail_com",
    "Dropmail_me": "dropmail_me",
    "Emaildashfake_com": "emaildashfake_com",
    "Emaildashfree_online": "emaildashfree_online",
    "Emailfake_com": "emailfake_com",
    "Emailondeck_com": "emailondeck_com",
    "Emailtenmin_com": "emailtenmin_com",
    "Etempmail_com": "etempmail_com",
    "Etempmail_net": "etempmail_net",
    "Expressinboxhub_com": "expressinboxhub_com",
    "Eyepaste_com": "eyepaste_com",
    "Eztempmail_com": "eztempmail_com",
    "Fakemail_net": "fakemail_net",
    "Fakemailgenerator_com": "fakemailgenerator_com",
    "Fakermail_com": "fakermail_com",
    "Fmail_sbs": "fmail_sbs",
    "Fumail_co": "fumail_co",
    "Generator_email": "generator_email",
    "Getnada_cc": "getnada_cc",
    "Gmailcity_com": "gmailcity_com",
    "Guerillamail_com": "guerillamail_com",
    "Harakirimail_com": "harakirimail_com",
    "Haribu_net": "haribu_net",
    "Inboxes_com": "inboxes_com",
    "Inboxkitten_com": "inboxkitten_com",
    "Incognitomail_co": "incognitomail_co",
    "Internxt_com": "internxt_com",
    "Lroid_com": "lroid_com",
    "Luxusmail_org": "luxusmail_org",
    "Maidashtemp_com": "maidashtemp_com",
    "Mail_gw": "mail_gw",
    "Mail_td": "mail_td",
    "Mail_tm": "mail_tm",
    "Mailcatch_com": "mailcatch_com",
    "Maildax_com": "maildax_com",
    "Mailforspam_com": "mailforspam_com",
    "Mailfourqa_com": "mailfourqa_com",
    "Mailgolem_com": "mailgolem_com",
    "Mailhole_de": "mailhole_de",
    "Mailinator_com": "mailinator_com",
    "Maillog_org": "maillog_org",
    "Mailnesia_com": "mailnesia_com",
    "Mailper_com": "mailper_com",
    "Mailsac_com": "mailsac_com",
    "Mailseven_io": "mailseven_io",
    "Mailtemp_net": "mailtemp_net",
    "Mailtemp_uk": "mailtemp_uk",
    "Mintemail_com": "mintemail_com",
    "Minuteinbox_com": "minuteinbox_com",
    "Minutemailbox_com": "minutemailbox_com",
    "Moakt_com": "moakt_com",
    "Mohamal_com": "mohmal_com",
    "Mohmal_com": "mohmal_com",
    "Mostakbile_com": "mostakbile_com",
    "Muellmail_com": "muellmail_com",
    "Nicemail_cc": "nicemail_cc",
    "Noopmail_org": "noopmail_org",
    "Onesecmail_com": "onesecmail_com",
    "Priyo_email": "priyo_email",
    "Rainmail_xyz": "rainmail_xyz",
    "Schutzdashmail_de": "schutzdashmail_de",
    "Segamail_com": "segamail_com",
    "Temils_com": "temils_com",
    "Tempail_com": "tempail_com",
    "Tempdashemail_info": "tempdashemail_info",
    "Tempdashinbox_com": "tempdashinbox_com",
    "Tempdashinbox_me": "tempdashinbox_me",
    "Tempdashmail_gg": "tempdashmail_gg",
    "Tempdashmail_id": "tempdashmail_id",
    "Tempdashmail_io": "tempdashmail_io",
    "Tempdashmail_org": "tempdashmail_org",
    "Tempdashmailbox_net": "tempdashmailbox_net",
    "Tempemail_co": "tempemail_co",
    "Tempemailfree_com": "tempemailfree_com",
    "Tempemailgen_com": "tempemailgen_com",
    "Tempinbox_xyz": "tempinbox_xyz",
    "Tempm_com": "tempm_com",
    "Tempmail_cc": "tempmail_cc",
    "Tempmail_email": "tempmail_email",
    "Tempmail_gg": "tempmail_gg",
    "Tempmail_guru": "tempmail_guru",
    "Tempmail_lol": "tempmail_lol",
    "Tempmail_net": "tempmail_net",
    "Tempmail_ninja": "tempmail_ninja",
    "Tempmail_plus": "tempmail_plus",
    "Tempmailbeast_com": "tempmailbeast_com",
    "Tempmailbox_net": "tempmailbox_net",
    "Tempmailer_net": "tempmailer_net",
    "Tempmailers_com": "tempmailers_com",
    "Tempmailinbox_com": "tempmailinbox_com",
    "Tempmails_net": "tempmails_net",
    "Tempmailso_com": "tempmailso_com",
    "Tempomail_com": "tempomail_com",
    "Tempomail_top": "tempomail_top",
    "Temporarymail_com": "temporarymail_com",
    "Temppdashmails_com": "temppdashmails_com",
    "Tempr_email": "tempr_email",
    "Tendashminutemail_net": "tendashminutemail_net",
    "Tenminemail_com": "tenminemail_com",
    "Tenminuteemail_com": "tenminuteemail_com",
    "Tenminuteemails_com": "tenminuteemails_com",
    "Tenminutemail_one": "tenminutemail_one",
    "Tenminutesemail_net": "tenminutesemail_net",
    "Tmail_ai": "tmail_ai",
    "Tmail_gg": "tmail_gg",
    "Tmail_io": "tmail_io",
    "Tmailor_com": "tmailor_com",
    "Tmdashmail_com": "tmdashmail_com",
    "Tmpmail_co": "tmpmail_co",
    "Trashmail_com": "trashmail_com",
    "Trashmail_de": "trashmail_de",
    "Trashmail_ws": "trashmail_ws",
    "Treemail_pro": "treemail_pro",
    "Txen_de": "txen_de",
    "Upxmail_com": "upxmail_com",
    "Wpdashtempmail_com": "wpdashtempmail_com",
    "Yopmail_com": "yopmail_com",
    "Zemail_me": "zemail_me"
}

def __getattr__(name):
    if name in _provider_map:
        module = importlib.import_module(f".providers.{_provider_map[name]}", __name__)
        attr = getattr(module, name)
        globals()[name] = attr
        return attr
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = list(_provider_map.keys())
__version = "2.2.0"