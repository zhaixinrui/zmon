import web
import urllib

SSO_URL = 'http://www.xxx.com:8100'

def auth():
    sso_username = web.config.session.get('sso_username')
    if sso_username:
        return sso_username
    service_url = '%s/sso?u=%s' % (web.ctx.homedomain, web.urlquote(web.ctx.homepath + web.ctx.fullpath))
    raise web.seeother('%s/login?service=%s' % (SSO_URL, web.urlquote(service_url)))

class sso:
    def GET(self):
        user_data = web.input(u=None, ticket=None)
        if not user_data.u or not user_data.ticket:
            return render.forbidden(userName)
        service_url = '%s/sso?u=%s' % (web.ctx.homedomain, web.urlquote(user_data.u))
        validate_url = '%s/validate?service=%s&ticket=%s' % (SSO_URL, web.urlquote(service_url), web.urlquote(user_data.ticket))
        r = urllib.urlopen(validate_url).readlines()
        if len(r) == 2 and r[0].strip() == 'yes':
            web.config.session.sso_username = r[1].strip()
            raise web.seeother(user_data.u)
        else:
            return render.forbidden(userName)
