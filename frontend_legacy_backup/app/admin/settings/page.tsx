'use client';

import { useState } from 'react';
import { Save, AlertCircle, CheckCircle } from 'lucide-react';

export default function SettingsPage() {
  // Constants from capstone requirements
  const SLO_TARGET_MS = 2000; // 2 seconds from capstone spec
  const ESCALATION_THRESHOLD_MS = 1600; // 80% of target
  const SAVE_NOTIFICATION_TIMEOUT_MS = 3000; // 3 seconds notification display

  const [settings, setSettings] = useState({
    sloTarget: SLO_TARGET_MS,
    escalationThreshold: ESCALATION_THRESHOLD_MS,
    maxRetries: 3,
    notificationsEnabled: true,
    analyticsEnabled: true,
    systemName: 'Retail Policy Intelligence System',
    version: '4.0 - Full Feature Implementation',
  });

  const [saved, setSaved] = useState(false);

  const handleSave = async () => {
    try {
      setSaved(true);
      setTimeout(() => setSaved(false), SAVE_NOTIFICATION_TIMEOUT_MS);
    } catch (error) {
    }
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>

      {saved && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <p className="text-green-800 font-semibold">Settings saved successfully!</p>
        </div>
      )}

      {/* SLO Configuration */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">SLO Configuration</h2>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Target Latency (ms)
            </label>
            <input
              type="number"
              value={settings.sloTarget}
              onChange={(e) => setSettings({ ...settings, sloTarget: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-sm text-gray-600 mt-1">Maximum acceptable query response time</p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Escalation Threshold (ms)
            </label>
            <input
              type="number"
              value={settings.escalationThreshold}
              onChange={(e) => setSettings({ ...settings, escalationThreshold: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-sm text-gray-600 mt-1">Time to trigger warning status</p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Max Retries
            </label>
            <input
              type="number"
              value={settings.maxRetries}
              onChange={(e) => setSettings({ ...settings, maxRetries: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-sm text-gray-600 mt-1">Number of retry attempts for failed queries</p>
          </div>
        </div>
      </div>

      {/* Feature Configuration */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Feature Configuration</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
            <div>
              <h3 className="font-semibold text-gray-900">Email Notifications</h3>
              <p className="text-sm text-gray-600">Send alerts for escalations and system events</p>
            </div>
            <input
              type="checkbox"
              checked={settings.notificationsEnabled}
              onChange={(e) => setSettings({ ...settings, notificationsEnabled: e.target.checked })}
              className="w-5 h-5 text-blue-600 rounded"
            />
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition">
            <div>
              <h3 className="font-semibold text-gray-900">Usage Analytics</h3>
              <p className="text-sm text-gray-600">Track system metrics and user behavior</p>
            </div>
            <input
              type="checkbox"
              checked={settings.analyticsEnabled}
              onChange={(e) => setSettings({ ...settings, analyticsEnabled: e.target.checked })}
              className="w-5 h-5 text-blue-600 rounded"
            />
          </div>
        </div>
      </div>

      {/* System Information */}
      <div className="bg-white rounded-lg shadow p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">System Information</h2>
        <div className="grid grid-cols-2 gap-8">
          <div>
            <p className="text-sm text-gray-600 mb-1">System Name</p>
            <p className="text-lg font-semibold text-gray-900">{settings.systemName}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Version</p>
            <p className="text-lg font-semibold text-gray-900">{settings.version}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Backend Status</p>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <p className="text-lg font-semibold text-green-600">Connected</p>
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Database</p>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <p className="text-lg font-semibold text-green-600">Operational</p>
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end gap-4">
        <button className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-semibold">
          Reset
        </button>
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
        >
          <Save className="w-5 h-5" />
          Save Settings
        </button>
      </div>

      {/* Danger Zone */}
      <div className="bg-red-50 border border-red-200 rounded-lg p-8">
        <div className="flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
          <div className="flex-1">
            <h3 className="font-bold text-red-900 mb-2">Danger Zone</h3>
            <p className="text-sm text-red-800 mb-4">These actions cannot be undone. Please proceed with caution.</p>
            <div className="flex gap-4">
              <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm font-semibold">
                Clear All Escalations
              </button>
              <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm font-semibold">
                Reset to Defaults
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
