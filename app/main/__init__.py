from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission

"""
1.上下文处理器应该返回一个字典，字典中的key会被模板中当成变量来渲染
2.上下文处理器返回的字典，在所有页面中都是可以使用的
3.被这个装饰器修饰的钩子函数，必须要返回一个字典，即使为空也要返回。
"""
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
