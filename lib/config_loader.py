import json


class Config:
    def __init__(self):
        self.TASK = None

    @classmethod
    def from_json(cls, json_file):
        instance = cls()
        with open(json_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # 创建TASK对象
        task_data = config_data['TASK']
        instance.TASK = type('TASK', (), {})()
        
        # 处理基本属性
        for key, value in task_data.items():
            if key != 'API':
                setattr(instance.TASK, key, value)
        
        # 处理API配置
        if 'API' in task_data:
            api_obj = type('API', (), {})()
            for api_name, api_config in task_data['API'].items():
                # 为每个API端点创建对象
                endpoint_obj = type(api_name, (), api_config)()
                setattr(api_obj, api_name, endpoint_obj)
            setattr(instance.TASK, 'API', api_obj)
        
        instance.json_file = json_file
        return instance

    def save(self):
        """保存配置到文件"""
        try:
            # 读取现有配置
            with open(self.json_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 只更新COOKIE值
            config_data['TASK']['COOKIE'] = self.TASK.COOKIE
            
            # 写入文件
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False
