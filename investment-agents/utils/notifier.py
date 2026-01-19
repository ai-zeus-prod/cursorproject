"""
Notification system for sending alerts via email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
from loguru import logger

from config.settings import settings


class Notifier:
    """Send notifications via email and other channels"""

    def __init__(self):
        self.email_enabled = settings.EMAIL_NOTIFICATIONS_ENABLED
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.user_email = settings.USER_EMAIL
        self.user_name = settings.USER_NAME

    def send_email(self, subject: str, body: str, html: bool = False) -> bool:
        """
        Send an email notification

        Args:
            subject: Email subject
            body: Email body (plain text or HTML)
            html: If True, body is treated as HTML

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.email_enabled:
            logger.info(f"Email notifications disabled. Would have sent: {subject}")
            return False

        if not self.smtp_username or not self.smtp_password:
            logger.warning("Email credentials not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = self.user_email

            # Attach body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def send_morning_briefing(self, opportunities: List[dict], portfolio_summary: dict) -> bool:
        """
        Send morning briefing with opportunities and portfolio status

        Args:
            opportunities: List of opportunity dictionaries
            portfolio_summary: Portfolio summary dictionary

        Returns:
            True if sent successfully
        """
        subject = f"📊 Morning Brief - {datetime.now().strftime('%Y-%m-%d')}"

        # Build HTML email
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: #4CAF50; color: white; padding: 10px; text-align: center; }}
                    .section {{ margin: 20px 0; padding: 10px; border: 1px solid #ddd; }}
                    .opportunity {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                    .score {{ font-size: 24px; font-weight: bold; color: #4CAF50; }}
                    .metric {{ display: inline-block; margin: 5px 10px; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #4CAF50; color: white; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Good Morning, {self.user_name}! ☀️</h1>
                    <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
                </div>

                <div class="section">
                    <h2>🎯 Top Opportunities ({len(opportunities)})</h2>
        """

        if opportunities:
            for opp in opportunities[:5]:  # Top 5
                html += f"""
                    <div class="opportunity">
                        <h3>{opp.get('symbol', 'N/A')} - {opp.get('company_name', 'N/A')}</h3>
                        <div class="score">Score: {opp.get('total_score', 0):.0f}/100</div>
                        <div>
                            <span class="metric">📈 Fundamental: {opp.get('fundamental_score', 0):.0f}</span>
                            <span class="metric">📊 Technical: {opp.get('technical_score', 0):.0f}</span>
                            <span class="metric">🏭 Sector: {opp.get('sector', 'N/A')}</span>
                        </div>
                        <div style="margin-top: 10px;">
                            <strong>Recommendation:</strong> {opp.get('recommendation', 'N/A')}<br/>
                            <strong>Pattern:</strong> {opp.get('pattern_matched', 'None detected')}<br/>
                            <strong>Reasoning:</strong> {opp.get('reasoning', 'N/A')}
                        </div>
                    </div>
                """
        else:
            html += "<p>No high-scoring opportunities found today.</p>"

        html += """
                </div>

                <div class="section">
                    <h2>💼 Portfolio Summary</h2>
                    <table>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
        """

        html += f"""
                        <tr><td>Total Trades</td><td>{portfolio_summary.get('total_trades', 0)}</td></tr>
                        <tr><td>Wins</td><td>{portfolio_summary.get('wins', 0)}</td></tr>
                        <tr><td>Win Rate</td><td>{portfolio_summary.get('win_rate', 0):.1f}%</td></tr>
                        <tr><td>Total P&L</td><td>₹{portfolio_summary.get('total_pnl', 0):,.2f}</td></tr>
                        <tr><td>Avg Win</td><td>{portfolio_summary.get('avg_win_percent', 0):.1f}%</td></tr>
                        <tr><td>Avg Loss</td><td>{portfolio_summary.get('avg_loss_percent', 0):.1f}%</td></tr>
                    </table>
                </div>

                <div class="section">
                    <p style="text-align: center; color: #666;">
                        📱 View full dashboard: <a href="http://localhost:{settings.DASHBOARD_PORT}">Open Dashboard</a>
                    </p>
                </div>
            </body>
        </html>
        """

        return self.send_email(subject, html, html=True)

    def send_alert(self, alert_type: str, symbol: str, message: str, level: str = "INFO") -> bool:
        """
        Send an immediate alert

        Args:
            alert_type: Type of alert (e.g., 'BREAKOUT', 'STOP_LOSS', 'TARGET_HIT')
            symbol: Stock symbol
            message: Alert message
            level: Alert level ('INFO', 'WARNING', 'CRITICAL')

        Returns:
            True if sent successfully
        """
        emoji = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'CRITICAL': '🚨'
        }.get(level, 'ℹ️')

        subject = f"{emoji} {alert_type}: {symbol}"

        body = f"""
{emoji} {alert_type} Alert

Stock: {symbol}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Level: {level}

Message:
{message}

---
Investment Agent System
        """

        return self.send_email(subject, body)

    def send_eod_report(self, portfolio_performance: dict, alerts: List[dict]) -> bool:
        """
        Send end-of-day report

        Args:
            portfolio_performance: Dictionary with performance metrics
            alerts: List of alert dictionaries

        Returns:
            True if sent successfully
        """
        subject = f"📈 EOD Report - {datetime.now().strftime('%Y-%m-%d')}"

        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .header {{ background-color: #2196F3; color: white; padding: 10px; text-align: center; }}
                    .section {{ margin: 20px 0; padding: 10px; border: 1px solid #ddd; }}
                    .positive {{ color: green; font-weight: bold; }}
                    .negative {{ color: red; font-weight: bold; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                    th {{ background-color: #2196F3; color: white; }}
                    .alert-box {{ background-color: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>End of Day Report 📊</h1>
                    <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
                </div>

                <div class="section">
                    <h2>📊 Today's Performance</h2>
                    <table>
                        <tr><td>Daily P&L</td><td class="{'positive' if portfolio_performance.get('daily_pnl', 0) >= 0 else 'negative'}">
                            ₹{portfolio_performance.get('daily_pnl', 0):,.2f}
                        </td></tr>
                        <tr><td>Open Positions</td><td>{portfolio_performance.get('open_positions', 0)}</td></tr>
                        <tr><td>Positions on Track</td><td>{portfolio_performance.get('on_track', 0)}</td></tr>
                        <tr><td>Positions Needing Review</td><td>{portfolio_performance.get('needs_review', 0)}</td></tr>
                    </table>
                </div>
        """

        if alerts:
            html += """
                <div class="section">
                    <h2>⚠️ Alerts Today</h2>
            """
            for alert in alerts:
                html += f"""
                    <div class="alert-box">
                        <strong>{alert.get('symbol', 'N/A')}</strong>: {alert.get('message', 'N/A')}
                    </div>
                """
            html += "</div>"

        html += """
                <div class="section">
                    <p style="text-align: center; color: #666;">
                        Have a great evening! 🌙
                    </p>
                </div>
            </body>
        </html>
        """

        return self.send_email(subject, html, html=True)

    def test_notification(self) -> bool:
        """Send a test notification to verify setup"""
        subject = "✅ Test Notification - Investment Agent System"
        body = f"""
Hello {self.user_name}!

This is a test notification from your Investment Agent System.

If you're receiving this email, your notification system is configured correctly! 🎉

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Your Investment Agent System
        """

        return self.send_email(subject, body)
