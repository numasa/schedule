# スケジューラーアプリケーション
![scheduler](https://user-images.githubusercontent.com/55865542/66189884-bf10b600-e6c5-11e9-96a0-e0e08a009aa7.png)

## AWS上で挙動します
scheduler.htmlはS3に配置します。
scheduler_entryはS3アップロードトリガーで実行されます。
scheduler_department,scheduler_member,schedule_eventはAPI Gatewayで実行されます。
![scheduler_architecture](https://user-images.githubusercontent.com/55865542/66191561-9c809c00-e6c9-11e9-95dc-6bc3163f1084.png)
