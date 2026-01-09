"""
Seed demo data for MemoScribe.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class Command(BaseCommand):
    help = "Seed demo data for testing"

    def handle(self, *args, **options):
        # Get or create demo user
        user, created = User.objects.get_or_create(
            username="demo",
            defaults={
                "email": "demo@example.com",
                "is_staff": False,
            },
        )
        if created:
            user.set_password("demo1234")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created demo user (demo/demo1234)"))

        # Create notes
        from notes.models import Note

        notes_data = [
            {
                "title": "プロジェクト計画",
                "body": "## 目標\n- Q1: 基盤構築\n- Q2: 機能開発\n- Q3: テスト\n- Q4: リリース\n\n優先順位は品質 > スケジュール",
                "tags": ["仕事", "計画"],
                "importance": 4,
            },
            {
                "title": "読書メモ: 効果的な習慣",
                "body": "1. 小さく始める\n2. 環境を整える\n3. 習慣をスタックする\n4. 報酬を設定する",
                "tags": ["読書", "自己啓発"],
                "importance": 3,
            },
            {
                "title": "アイデアメモ",
                "body": "- 自動化ツールの開発\n- データ可視化ダッシュボード\n- 音声入力対応",
                "tags": ["アイデア", "開発"],
                "importance": 2,
            },
        ]

        for data in notes_data:
            Note.objects.get_or_create(
                user=user,
                title=data["title"],
                defaults=data,
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(notes_data)} notes"))

        # Create daily logs
        from logs.models import DailyLog, DailyDigest

        today = timezone.now().date()
        logs_data = [
            {
                "date": today - datetime.timedelta(days=2),
                "raw_text": "今日は朝から会議が3つあった。プロジェクトの進捗報告と来週のスケジュール調整。午後はコードレビューに集中できた。夜は早めに帰宅して本を読んだ。",
                "mood": 4,
            },
            {
                "date": today - datetime.timedelta(days=1),
                "raw_text": "昨日の疲れが残っていてスロースタート。でも午後から調子が出てきて、重要なバグを修正できた。チームメンバーとランチに行って良い情報交換ができた。",
                "mood": 3,
            },
            {
                "date": today,
                "raw_text": "今日は集中して作業できた。新機能の設計書を完成させた。明日はコーディングに着手する予定。健康のために30分散歩した。",
                "mood": 5,
            },
        ]

        for data in logs_data:
            log, created = DailyLog.objects.get_or_create(
                user=user,
                date=data["date"],
                defaults=data,
            )
            if created:
                # Create digest manually for demo
                DailyDigest.objects.create(
                    user=user,
                    log=log,
                    summary=f"{data['date']}の記録。{data['raw_text'][:50]}...",
                    tags=["仕事", "日常"],
                    topics=["業務", "健康"],
                    actions=["タスクを確認", "休息を取る"],
                )
        self.stdout.write(self.style.SUCCESS(f"Created {len(logs_data)} daily logs with digests"))

        # Create tasks
        from tasks.models import Task

        tasks_data = [
            {
                "title": "週次レポート作成",
                "description": "今週の進捗と来週の計画をまとめる",
                "due_at": timezone.now() + datetime.timedelta(days=2),
                "priority": 3,
                "status": "todo",
                "tags": ["仕事", "定期"],
            },
            {
                "title": "ドキュメント更新",
                "description": "API仕様書を最新に更新する",
                "due_at": timezone.now() + datetime.timedelta(days=5),
                "priority": 2,
                "status": "doing",
                "tags": ["仕事", "開発"],
            },
            {
                "title": "健康診断予約",
                "description": "年次健康診断の予約を入れる",
                "due_at": timezone.now() + datetime.timedelta(days=7),
                "priority": 2,
                "status": "todo",
                "tags": ["健康", "個人"],
            },
        ]

        for data in tasks_data:
            Task.objects.get_or_create(
                user=user,
                title=data["title"],
                defaults=data,
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(tasks_data)} tasks"))

        # Create preferences
        from preferences.models import Preference

        prefs_data = [
            {
                "key": "文章スタイル",
                "value": "丁寧でフォーマルな文体を好む。敬語を適切に使用する。",
                "category": "writing",
            },
            {
                "key": "起床時間",
                "value": "朝6時に起床。朝型の生活リズム。",
                "category": "lifestyle",
            },
            {
                "key": "意思決定ルール",
                "value": "健康を最優先。次に家族、仕事の順。長期的な視点を重視。",
                "category": "decision",
            },
            {
                "key": "仕事の方針",
                "value": "品質優先。締め切りより質を重視。チームワークを大切に。",
                "category": "work",
            },
        ]

        for data in prefs_data:
            Preference.objects.get_or_create(
                user=user,
                key=data["key"],
                defaults=data,
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(prefs_data)} preferences"))

        self.stdout.write(self.style.SUCCESS("\nDemo data seeded successfully!"))
        self.stdout.write("Login with: demo / demo1234")
