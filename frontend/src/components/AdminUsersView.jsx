import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Search, 
  Filter, 
  UserPlus, 
  Shield, 
  UserCheck, 
  UserX, 
  Edit3, 
  Clock, 
  Eye, 
  AlertTriangle, 
  ChevronLeft, 
  ChevronRight, 
  CheckCircle, 
  X,
  RefreshCw,
  Activity,
  Key
} from 'lucide-react';
import { 
  getAdminUsers, 
  getAdminUserDetail, 
  createAdminUser, 
  updateUserRole, 
  updateUserStatus 
} from '../api';

export default function AdminUsersView() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const limit = 10;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters & Sorting
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState(-1);

  // Modals
  const [selectedUserDetail, setSelectedUserDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isRoleModalOpen, setIsRoleModalOpen] = useState(false);
  const [isStatusConfirmOpen, setIsStatusConfirmOpen] = useState(false);
  const [targetUser, setTargetUser] = useState(null);

  // Form states
  const [createForm, setCreateForm] = useState({
    name: '',
    email: '',
    password: '',
    role: 'analyst',
    status: 'active'
  });
  const [targetNewRole, setTargetNewRole] = useState('analyst');
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAdminUsers({
        search,
        role: roleFilter,
        status: statusFilter,
        sort_by: sortBy,
        sort_order: sortOrder,
        page,
        limit
      });
      setUsers(res.users || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load user accounts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [page, roleFilter, statusFilter, sortBy, sortOrder]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchUsers();
  };

  const handleOpenDetail = async (user) => {
    setDetailLoading(true);
    setActionError(null);
    try {
      const res = await getAdminUserDetail(user.id || user.email);
      setSelectedUserDetail(res);
    } catch (err) {
      setActionError(err.message || 'Failed to load user telemetry profile.');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    setActionError(null);
    try {
      await createAdminUser(createForm);
      setIsCreateOpen(false);
      setCreateForm({ name: '', email: '', password: '', role: 'analyst', status: 'active' });
      setActionSuccess(`User account '${createForm.email}' provisioned successfully.`);
      fetchUsers();
    } catch (err) {
      setActionError(err.message || 'Failed to provision user.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRoleUpdate = async () => {
    if (!targetUser) return;
    setActionLoading(true);
    setActionError(null);
    try {
      await updateUserRole(targetUser.id || targetUser.email, targetNewRole);
      setIsRoleModalOpen(false);
      setActionSuccess(`Role for '${targetUser.email}' updated to '${targetNewRole.toUpperCase()}'.`);
      fetchUsers();
    } catch (err) {
      setActionError(err.message || 'Failed to update user role.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStatusToggle = async () => {
    if (!targetUser) return;
    const newStatus = targetUser.status === 'active' ? 'disabled' : 'active';
    setActionLoading(true);
    setActionError(null);
    try {
      await updateUserStatus(targetUser.id || targetUser.email, newStatus);
      setIsStatusConfirmOpen(false);
      setActionSuccess(`User account '${targetUser.email}' is now ${newStatus.toUpperCase()}.`);
      fetchUsers();
    } catch (err) {
      setActionError(err.message || 'Failed to toggle account status.');
    } finally {
      setActionLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Never';
    try {
      const d = new Date(dateStr);
      return d.toLocaleString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner & Provision Button */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
            <div style={{ background: 'rgba(6, 182, 212, 0.15)', padding: '0.45rem', borderRadius: '8px', border: '1px solid var(--accent-cyan)' }}>
              <Users size={22} color="#06b6d4" />
            </div>
            <h2 style={{ fontSize: '1.25rem', color: '#fff' }}>
              Enterprise User & Identity Governance
            </h2>
            <span className="badge badge-low" style={{ fontSize: '0.7rem' }}>
              {total} Total Users
            </span>
          </div>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
            Provision SOC personnel, configure role authorizations, toggle active/disabled states, and audit operator telemetry.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button 
            onClick={() => fetchUsers()} 
            className="btn btn-secondary" 
            title="Refresh list"
            style={{ padding: '0.6rem 0.85rem' }}
          >
            <RefreshCw size={16} />
          </button>
          <button 
            onClick={() => {
              setActionError(null);
              setIsCreateOpen(true);
            }} 
            className="btn btn-primary"
            id="btn-provision-user"
          >
            <UserPlus size={16} />
            <span>Provision SOC Account</span>
          </button>
        </div>
      </div>

      {/* Global Alerts */}
      {actionSuccess && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          color: '#34d399',
          padding: '0.85rem 1.25rem',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', fontSize: '0.85rem' }}>
            <CheckCircle size={18} />
            <span>{actionSuccess}</span>
          </div>
          <button onClick={() => setActionSuccess(null)} style={{ background: 'none', border: 'none', color: '#34d399', cursor: 'pointer' }}>
            <X size={16} />
          </button>
        </div>
      )}

      {error && (
        <div style={{
          background: 'rgba(244, 63, 94, 0.12)',
          border: '1px solid rgba(244, 63, 94, 0.4)',
          color: '#fda4af',
          padding: '0.85rem 1.25rem',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '0.65rem',
          fontSize: '0.85rem'
        }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.85rem' }}>
          <div style={{ flex: '1 1 240px', position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search user by name or email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-control"
              style={{ paddingLeft: '2.4rem' }}
              id="admin-search-users"
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Role:</label>
            <select 
              value={roleFilter} 
              onChange={(e) => { setRoleFilter(e.target.value); setPage(1); }}
              className="input-control"
              style={{ width: '130px' }}
              id="admin-filter-role"
            >
              <option value="all">All Roles</option>
              <option value="admin">Admin</option>
              <option value="analyst">Analyst</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Status:</label>
            <select 
              value={statusFilter} 
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="input-control"
              style={{ width: '130px' }}
              id="admin-filter-status"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="disabled">Disabled</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Sort By:</label>
            <select 
              value={sortBy} 
              onChange={(e) => setSortBy(e.target.value)}
              className="input-control"
              style={{ width: '150px' }}
              id="admin-sort-by"
            >
              <option value="created_at">Registered Date</option>
              <option value="last_login_at">Last Login</option>
              <option value="name">Name</option>
              <option value="login_count">Login Count</option>
            </select>
          </div>

          <button type="submit" className="btn btn-secondary" style={{ padding: '0.65rem 1rem' }}>
            Filter
          </button>
        </form>
      </div>

      {/* Users Table */}
      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <div className="soc-table-container">
          <table className="soc-table">
            <thead>
              <tr>
                <th>Operator Identity</th>
                <th>Role</th>
                <th>Status</th>
                <th>Registered</th>
                <th>Last Login</th>
                <th style={{ textAlign: 'center' }}>Logins (OK / Fail)</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    <RefreshCw className="spin" size={24} style={{ margin: '0 auto 0.5rem auto' }} />
                    <p>Loading security identities...</p>
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    No users matching criteria found.
                  </td>
                </tr>
              ) : (
                users.map((u) => {
                  const roleBadgeClass = u.role === 'admin' ? 'badge-critical' : (u.role === 'analyst' ? 'badge-medium' : 'badge-low');
                  const statusBadgeClass = u.status === 'active' ? 'badge-low' : 'badge-critical';
                  return (
                    <tr key={u.id || u.email}>
                      <td>
                        <div style={{ fontWeight: 600, color: '#fff' }}>{u.name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{u.email}</div>
                      </td>
                      <td>
                        <span className={`badge ${roleBadgeClass}`}>
                          {u.role}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${statusBadgeClass}`}>
                          {u.status}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        {formatDate(u.created_at)}
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        {formatDate(u.last_login_at)}
                      </td>
                      <td style={{ textAlign: 'center', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                        <span style={{ color: '#34d399', fontWeight: 600 }}>{u.login_count || 0}</span>
                        <span style={{ color: 'var(--text-muted)', margin: '0 0.3rem' }}>/</span>
                        <span style={{ color: (u.failed_login_count > 0 ? '#f87171' : 'var(--text-muted)'), fontWeight: 600 }}>
                          {u.failed_login_count || 0}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'inline-flex', gap: '0.4rem' }}>
                          <button
                            onClick={() => handleOpenDetail(u)}
                            className="btn btn-secondary"
                            title="Inspect Profile & Audit Activity"
                            style={{ padding: '0.35rem 0.6rem', fontSize: '0.75rem' }}
                          >
                            <Eye size={14} />
                          </button>
                          <button
                            onClick={() => {
                              setTargetUser(u);
                              setTargetNewRole(u.role);
                              setIsRoleModalOpen(true);
                              setActionError(null);
                            }}
                            className="btn btn-secondary"
                            title="Change Role"
                            style={{ padding: '0.35rem 0.6rem', fontSize: '0.75rem' }}
                          >
                            <Edit3 size={14} />
                          </button>
                          <button
                            onClick={() => {
                              setTargetUser(u);
                              setIsStatusConfirmOpen(true);
                              setActionError(null);
                            }}
                            className={u.status === 'active' ? 'btn btn-danger' : 'btn btn-secondary'}
                            title={u.status === 'active' ? 'Disable Account' : 'Activate Account'}
                            style={{ padding: '0.35rem 0.6rem', fontSize: '0.75rem' }}
                          >
                            {u.status === 'active' ? <UserX size={14} /> : <UserCheck size={14} color="#34d399" />}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.8rem',
          color: 'var(--text-secondary)'
        }}>
          <div>
            Showing Page <span style={{ color: '#fff', fontWeight: 600 }}>{page}</span> of <span style={{ color: '#fff', fontWeight: 600 }}>{totalPages}</span> ({total} accounts)
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              disabled={page <= 1 || loading}
              onClick={() => setPage(page - 1)}
              className="btn btn-secondary"
              style={{ padding: '0.4rem 0.75rem' }}
            >
              <ChevronLeft size={16} />
              <span>Previous</span>
            </button>
            <button
              disabled={page >= totalPages || loading}
              onClick={() => setPage(page + 1)}
              className="btn btn-secondary"
              style={{ padding: '0.4rem 0.75rem' }}
            >
              <span>Next</span>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* MODAL 1: Provision User */}
      {isCreateOpen && (
        <div className="modal-overlay" onClick={() => setIsCreateOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '480px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <UserPlus size={20} color="#06b6d4" />
                <h3 style={{ color: '#fff', fontSize: '1.15rem' }}>Provision SOC Account</h3>
              </div>
              <button onClick={() => setIsCreateOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {actionError && (
              <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid #f43f5e', padding: '0.75rem', borderRadius: '8px', color: '#fca5a5', fontSize: '0.8rem', marginBottom: '1rem' }}>
                {actionError}
              </div>
            )}

            <form onSubmit={handleCreateSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>Callsign / Full Name</label>
                <input
                  type="text"
                  required
                  value={createForm.name}
                  onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  placeholder="e.g. Officer Nathan Vance"
                  className="input-control"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>Email Address</label>
                <input
                  type="email"
                  required
                  value={createForm.email}
                  onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                  placeholder="nvance@soc.defense.gov"
                  className="input-control"
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>Initial Password</label>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={createForm.password}
                  onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                  placeholder="Minimum 6 characters"
                  className="input-control"
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>Role</label>
                  <select
                    value={createForm.role}
                    onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
                    className="input-control"
                  >
                    <option value="analyst">Analyst</option>
                    <option value="admin">Administrator</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>Status</label>
                  <select
                    value={createForm.status}
                    onChange={(e) => setCreateForm({ ...createForm, status: e.target.value })}
                    className="input-control"
                  >
                    <option value="active">Active</option>
                    <option value="disabled">Disabled</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" onClick={() => setIsCreateOpen(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={actionLoading} className="btn btn-primary">
                  {actionLoading ? 'Provisioning...' : 'Confirm Provisioning'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: Change User Role */}
      {isRoleModalOpen && targetUser && (
        <div className="modal-overlay" onClick={() => setIsRoleModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '440px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <Shield size={20} color="#8b5cf6" />
                <h3 style={{ color: '#fff', fontSize: '1.15rem' }}>Change Role Authorization</h3>
              </div>
              <button onClick={() => setIsRoleModalOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {actionError && (
              <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid #f43f5e', padding: '0.75rem', borderRadius: '8px', color: '#fca5a5', fontSize: '0.8rem', marginBottom: '1rem' }}>
                {actionError}
              </div>
            )}

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '8px', marginBottom: '1rem', fontSize: '0.825rem' }}>
              <div>Target User: <strong style={{ color: '#fff' }}>{targetUser.email}</strong></div>
              <div>Current Role: <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>{targetUser.role.toUpperCase()}</span></div>
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                Select New Role:
              </label>
              <select
                value={targetNewRole}
                onChange={(e) => setTargetNewRole(e.target.value)}
                className="input-control"
              >
                <option value="viewer">Viewer (Read-only)</option>
                <option value="analyst">Analyst (Operational)</option>
                <option value="admin">Admin (Full Control)</option>
              </select>
            </div>

            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
              Note: System enforces Last-Admin Protection. You cannot demote the final remaining administrator.
            </p>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button onClick={() => setIsRoleModalOpen(false)} className="btn btn-secondary">
                Cancel
              </button>
              <button onClick={handleRoleUpdate} disabled={actionLoading} className="btn btn-primary">
                {actionLoading ? 'Updating...' : 'Confirm Role Change'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: Enable/Disable Account Confirmation */}
      {isStatusConfirmOpen && targetUser && (
        <div className="modal-overlay" onClick={() => setIsStatusConfirmOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '440px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1rem' }}>
              <AlertTriangle size={22} color={targetUser.status === 'active' ? '#f43f5e' : '#10b981'} />
              <h3 style={{ color: '#fff', fontSize: '1.15rem' }}>
                {targetUser.status === 'active' ? 'Confirm Disable Account' : 'Confirm Activate Account'}
              </h3>
            </div>

            {actionError && (
              <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid #f43f5e', padding: '0.75rem', borderRadius: '8px', color: '#fca5a5', fontSize: '0.8rem', marginBottom: '1rem' }}>
                {actionError}
              </div>
            )}

            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
              {targetUser.status === 'active' ? (
                <>
                  Are you sure you want to <strong>DISABLE</strong> user <strong>{targetUser.email}</strong>? The user will immediately be barred from signing in and generating JWT access tokens.
                </>
              ) : (
                <>
                  Are you sure you want to <strong>ACTIVATE</strong> user <strong>{targetUser.email}</strong>? The account will be restored with full operational permissions.
                </>
              )}
            </p>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button onClick={() => setIsStatusConfirmOpen(false)} className="btn btn-secondary">
                Cancel
              </button>
              <button
                onClick={handleStatusToggle}
                disabled={actionLoading}
                className={targetUser.status === 'active' ? 'btn btn-danger' : 'btn btn-primary'}
              >
                {actionLoading ? 'Updating...' : (targetUser.status === 'active' ? 'Disable Account' : 'Activate Account')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 4: User Profile & Activity Telemetry (Feature 8) */}
      {selectedUserDetail && (
        <div className="modal-overlay" onClick={() => setSelectedUserDetail(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '680px', maxHeight: '85vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.85rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ background: 'rgba(6, 182, 212, 0.15)', padding: '0.5rem', borderRadius: '10px' }}>
                  <Users size={22} color="#06b6d4" />
                </div>
                <div>
                  <h3 style={{ color: '#fff', fontSize: '1.2rem' }}>{selectedUserDetail.user.name}</h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    {selectedUserDetail.user.email} • ID: {selectedUserDetail.user.id}
                  </p>
                </div>
              </div>
              <button onClick={() => setSelectedUserDetail(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {/* Profile Statistics Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.85rem', marginBottom: '1.5rem' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>ROLE</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--accent-cyan)', textTransform: 'capitalize' }}>
                  {selectedUserDetail.user.role}
                </div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>STATUS</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 600, color: selectedUserDetail.user.status === 'active' ? '#34d399' : '#f87171', textTransform: 'capitalize' }}>
                  {selectedUserDetail.user.status}
                </div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>LOGINS</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#34d399' }}>
                  {selectedUserDetail.user.login_count || 0}
                </div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>FAILED LOGINS</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 600, color: selectedUserDetail.user.failed_login_count > 0 ? '#f87171' : 'var(--text-muted)' }}>
                  {selectedUserDetail.user.failed_login_count || 0}
                </div>
              </div>
            </div>

            {/* Timestamps */}
            <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '0.85rem', borderRadius: '8px', marginBottom: '1.5rem', fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              <div>📅 <strong style={{ color: 'var(--text-secondary)' }}>Registered:</strong> {formatDate(selectedUserDetail.user.created_at)}</div>
              <div>🔑 <strong style={{ color: 'var(--text-secondary)' }}>Last Login:</strong> {formatDate(selectedUserDetail.user.last_login_at)}</div>
              <div>🚪 <strong style={{ color: 'var(--text-secondary)' }}>Last Logout:</strong> {formatDate(selectedUserDetail.user.last_logout_at)}</div>
            </div>

            {/* Recent Activity Timeline */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
                <Activity size={18} color="#06b6d4" />
                <h4 style={{ color: '#fff', fontSize: '0.95rem' }}>Recent Security Activity Timeline</h4>
              </div>

              {selectedUserDetail.recent_activity.length === 0 ? (
                <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  No security audit records logged for this user identity yet.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {selectedUserDetail.recent_activity.map((act, i) => (
                    <div 
                      key={act.id || i}
                      style={{
                        background: 'rgba(15, 23, 42, 0.6)',
                        borderLeft: `3px solid ${act.status === 'success' ? '#10b981' : '#f43f5e'}`,
                        padding: '0.65rem 0.85rem',
                        borderRadius: '0 8px 8px 0',
                        fontSize: '0.775rem'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                        <span style={{ fontWeight: 600, color: '#fff' }}>{act.action}</span>
                        <span style={{ color: 'var(--text-muted)' }}>{formatDate(act.timestamp)}</span>
                      </div>
                      <div style={{ color: 'var(--text-secondary)', display: 'flex', gap: '0.85rem' }}>
                        <span>Resource: <strong style={{ color: 'var(--accent-cyan)' }}>{act.resource_type || 'N/A'}</strong></span>
                        <span>IP: <code style={{ color: 'var(--text-muted)' }}>{act.ip_address}</code></span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
              <button onClick={() => setSelectedUserDetail(null)} className="btn btn-secondary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
