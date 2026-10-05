import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Users, 
  Key, 
  Shield, 
  FileText, 
  LayoutDashboard 
} from 'lucide-react';
import AdminDashboardView from './AdminDashboardView';
import AdminUsersView from './AdminUsersView';
import LoginHistoryView from './LoginHistoryView';
import AuditLogsView from './AuditLogsView';
import ReportsView from './ReportsView';

export default function AdminConsole({ initialSubTab = 'dashboard', currentUser }) {
  const [activeSubTab, setActiveSubTab] = useState(initialSubTab);

  const subTabs = [
    { id: 'dashboard', label: 'Security Console', icon: LayoutDashboard },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'login-history', label: 'Login History', icon: Key },
    { id: 'audit-logs', label: 'Audit Trail', icon: Shield },
    { id: 'reports-history', label: 'Report History', icon: FileText },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Sub-navigation Tabs */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.4rem',
        background: 'rgba(15, 23, 42, 0.75)',
        padding: '0.4rem',
        borderRadius: '12px',
        border: '1px solid var(--border-subtle)',
        flexWrap: 'wrap'
      }}>
        {subTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeSubTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              id={`admin-subtab-${tab.id}`}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.55rem 1.15rem',
                borderRadius: '8px',
                border: 'none',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                background: isActive 
                  ? 'linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(59, 130, 246, 0.25) 100%)' 
                  : 'transparent',
                color: isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                borderBottom: isActive ? '2px solid var(--accent-cyan)' : '2px solid transparent'
              }}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Render Active View */}
      {activeSubTab === 'dashboard' && (
        <AdminDashboardView onNavigateTab={(target) => setActiveSubTab(target)} />
      )}

      {activeSubTab === 'users' && (
        <AdminUsersView />
      )}

      {activeSubTab === 'login-history' && (
        <LoginHistoryView />
      )}

      {activeSubTab === 'audit-logs' && (
        <AuditLogsView />
      )}

      {activeSubTab === 'reports-history' && (
        <ReportsView currentUser={currentUser} />
      )}
    </div>
  );
}
