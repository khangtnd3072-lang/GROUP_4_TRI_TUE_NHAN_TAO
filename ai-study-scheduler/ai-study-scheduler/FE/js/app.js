import { api } from './api.js';

const state = {
  dashboard: {},
  subjects: [],
  tasks: [],
  availability: [],
  sessions: [],
  aiResult: null,
};

const $ = (selector) => document.querySelector(selector);

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function formatDate(value) {
  if (!value) return '–';
  const date = new Date(`${value}T00:00:00`);
  return new Intl.DateTimeFormat('vi-VN', {
    weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric',
  }).format(date);
}

function formatDateTime(value) {
  if (!value) return '–';
  const normalized = String(value).includes('T') ? value : String(value).replace(' ', 'T');
  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) return escapeHtml(value);
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit',
  }).format(date);
}

function shortTime(value) {
  return String(value || '').slice(0, 5);
}

function statusLabel(status) {
  return ({
    pending: 'Chờ xử lý',
    in_progress: 'Đang học',
    completed: 'Hoàn thành',
    planned: 'Đã lên lịch',
    missed: 'Bỏ lỡ',
  })[status] || status;
}

function notify(text, type = 'success') {
  const host = $('#toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = text;
  host.replaceChildren(toast);
  window.setTimeout(() => {
    if (toast.isConnected) toast.remove();
  }, 3800);
}

async function loadAll() {
  try {
    const [dashboard, subjects, tasks, availability, sessions] = await Promise.all([
      api.dashboard(), api.subjects(), api.tasks(), api.availability(), api.schedule(),
    ]);
    Object.assign(state, { dashboard, subjects, tasks, availability, sessions });
    renderAll();
  } catch (error) {
    notify(`Không kết nối được Backend/MySQL: ${error.message}`, 'error');
  }
}

function renderAll() {
  renderStats();
  renderSubjects();
  renderSubjectSelect();
  renderAvailability();
  renderTasks();
  renderAIResult();
  renderTimeline();
}

function renderStats() {
  const d = state.dashboard;
  const stats = [
    ['Môn học', d.subjects ?? 0, ''],
    ['Study Task', d.tasks ?? 0, ''],
    ['Task chưa xong', d.pending_tasks ?? 0, ''],
    ['Phiên đã lập lịch', d.sessions ?? 0, ''],
  ];

  const cards = stats.map(([label, value, note]) => `
    <article class="stat-card">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      ${note ? `<small>${escapeHtml(note)}</small>` : ''}
    </article>
  `).join('');

  $('#stats-grid').innerHTML = cards + `
    <article class="stat-card rule-card">
      <span>Quy tắc AI</span>
      <strong>${escapeHtml(d.max_study_hours_per_day ?? 3)}h/ngày</strong>
      <small>Slot ${escapeHtml(d.slot_minutes ?? 30)} phút · Mỗi phiên ≤ ${escapeHtml(d.max_session_hours ?? 2)}h</small>
    </article>
  `;
}

function renderSubjects() {
  const host = $('#subject-list');
  if (!state.subjects.length) {
    host.innerHTML = '<span class="empty">Chưa có môn học.</span>';
    return;
  }
  host.innerHTML = state.subjects.map((subject) => `
    <span class="chip">${escapeHtml(subject.name)} · P${escapeHtml(subject.priority)} · D${escapeHtml(subject.difficulty)}</span>
  `).join('');
}

function renderSubjectSelect() {
  const select = $('#task-subject');
  if (!state.subjects.length) {
    select.innerHTML = '<option value="">Hãy thêm môn học trước</option>';
    select.disabled = true;
    return;
  }
  const previous = select.value;
  select.disabled = false;
  select.innerHTML = state.subjects.map((subject) => `
    <option value="${subject.id}">${escapeHtml(subject.name)}</option>
  `).join('');
  if (previous && state.subjects.some((subject) => String(subject.id) === previous)) {
    select.value = previous;
  }
}

function renderAvailability() {
  const host = $('#availability-list');
  if (!state.availability.length) {
    host.innerHTML = '<span class="empty">Chưa khai báo thời gian rảnh.</span>';
    return;
  }
  host.innerHTML = state.availability.map((item) => `
    <div class="list-row">
      <div>
        <strong>${escapeHtml(formatDate(item.study_date))}</strong>
        <small>${escapeHtml(shortTime(item.start_time))} – ${escapeHtml(shortTime(item.end_time))}</small>
      </div>
      <button class="ghost-danger" type="button" data-action="delete-availability" data-id="${item.id}">
        <span class="material-symbols-outlined icon-sm">delete</span> Xóa
      </button>
    </div>
  `).join('');
}

function renderTasks() {
  const body = $('#task-table-body');
  if (!state.tasks.length) {
    body.innerHTML = '<tr><td colspan="7" class="empty-cell">Chưa có Study Task.</td></tr>';
    return;
  }

  body.innerHTML = state.tasks.map((task) => `
    <tr>
      <td>${escapeHtml(task.subject_name)}</td>
      <td><strong>${escapeHtml(task.title)}</strong></td>
      <td>${escapeHtml(task.estimated_hours)}</td>
      <td>${escapeHtml(formatDateTime(task.deadline))}</td>
      <td>${escapeHtml(task.priority)}/${escapeHtml(task.difficulty)}</td>
      <td><span class="status ${escapeHtml(task.status)}">${escapeHtml(statusLabel(task.status))}</span></td>
      <td class="actions-cell">
        ${task.status !== 'completed'
          ? `<button class="tiny-btn" type="button" data-action="complete-task" data-id="${task.id}"><span class="material-symbols-outlined icon-sm">check</span> Hoàn thành</button>`
          : ''}
        <button class="ghost-danger" type="button" data-action="delete-task" data-id="${task.id}"><span class="material-symbols-outlined icon-sm">delete</span> Xóa</button>
      </td>
    </tr>
  `).join('');
}

function renderAIResult() {
  const host = $('#ai-result');
  const result = state.aiResult;
  if (!result) {
    host.innerHTML = '<div class="empty ai-empty">Bấm “Tạo lịch học bằng AI” để xem Fitness và so sánh với Earliest Deadline First.</div>';
    return;
  }

  const details = result.metrics?.task_details || [];
  host.innerHTML = `
    <div class="compare-grid">
      <article class="compare-card featured">
        <span>Genetic Algorithm</span>
        <strong>${Number(result.fitness).toFixed(2)}</strong>
        <small>Fitness · ${Math.round((result.metrics?.full_schedule_rate || 0) * 100)}% task đủ giờ</small>
      </article>
      <article class="compare-card">
        <span>EDF Baseline</span>
        <strong>${Number(result.baseline?.fitness || 0).toFixed(2)}</strong>
        <small>Fitness · ${Math.round((result.baseline?.metrics?.full_schedule_rate || 0) * 100)}% task đủ giờ</small>
      </article>
      <article class="compare-card">
        <span>Số thế hệ đã chạy</span>
        <strong>${escapeHtml(result.generations_run)}</strong>
        <small>Dừng sớm nếu nhiều thế hệ không cải thiện.</small>
      </article>
      <article class="compare-card">
        <span>Tổng giờ đã phân bổ</span>
        <strong>${escapeHtml(result.metrics?.allocated_hours ?? 0)}h</strong>
        <small>Ràng buộc tối đa 3 giờ/ngày.</small>
      </article>
    </div>
    <h3 class="mini-title">Priority Score theo Task</h3>
    <div class="priority-list">
      ${details.length ? details.map((item) => {
        const score = Math.max(0, Math.min(1, Number(item.priority_score || 0)));
        return `
          <div class="priority-item">
            <div>
              <strong>${escapeHtml(item.task_title)}</strong>
              <small>${escapeHtml(item.allocated_hours)}/${escapeHtml(item.required_hours)} giờ</small>
            </div>
            <div class="bar"><i style="width:${Math.round(score * 100)}%"></i></div>
            <b>${score.toFixed(3)}</b>
          </div>
        `;
      }).join('') : '<span class="empty">Không có dữ liệu Priority Score.</span>'}
    </div>
  `;
}

function renderTimeline() {
  const host = $('#timeline');
  if (!state.sessions.length) {
    host.innerHTML = '<div class="empty">Chưa có lịch học. Hãy nhập dữ liệu và chạy AI.</div>';
    return;
  }

  const grouped = state.sessions.reduce((result, session) => {
    (result[session.session_date] ||= []).push(session);
    return result;
  }, {});

  host.innerHTML = `<div class="timeline">${Object.entries(grouped).map(([date, sessions]) => `
    <div class="day-block">
      <div class="day-label">${escapeHtml(formatDate(date))}</div>
      <div class="day-sessions">
        ${sessions.map((session) => `
          <article class="session-card ${escapeHtml(session.status)}" data-session-card="${session.id}">
            <button class="session-main" type="button" data-action="toggle-session" data-id="${session.id}" aria-expanded="false">
              <span class="session-time">${escapeHtml(shortTime(session.start_time))} – ${escapeHtml(shortTime(session.end_time))}</span>
              <span class="session-body">
                <small>${escapeHtml(session.subject_name)}</small>
                <strong>${escapeHtml(session.task_title)}</strong>
                <em>${Number(session.duration_hours).toFixed(1)} giờ · ${escapeHtml(statusLabel(session.status))}</em>
              </span>
              <span class="chevron">+</span>
            </button>
            <div class="session-detail" data-session-detail="${session.id}" hidden>
              <div><b>Priority:</b> ${escapeHtml(session.priority)}/5 · <b>Difficulty:</b> ${escapeHtml(session.difficulty)}/5</div>
              ${session.notes ? `<p><b>Ghi chú:</b> ${escapeHtml(session.notes)}</p>` : ''}
              ${session.resource_link ? `<p><b>Tài liệu:</b> <a href="${escapeHtml(session.resource_link)}" target="_blank" rel="noopener noreferrer">Mở liên kết</a></p>` : ''}
              <div class="session-actions">
                ${session.status !== 'completed'
                  ? `<button class="tiny-btn" type="button" data-action="complete-session" data-id="${session.id}"><span class="material-symbols-outlined icon-sm">check_circle</span> Đánh dấu hoàn thành</button>`
                  : ''}
                ${session.status === 'planned'
                  ? `<button class="ghost-danger" type="button" data-action="miss-session" data-id="${session.id}"><span class="material-symbols-outlined icon-sm">cancel</span> Bỏ lỡ</button>`
                  : ''}
              </div>
            </div>
          </article>
        `).join('')}
      </div>
    </div>
  `).join('')}</div>`;
}

async function refreshAfterChange(successMessage) {
  state.aiResult = null;
  await loadAll();
  notify(successMessage);
}

$('#subject-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    await api.addSubject({
      name: $('#subject-name').value.trim(),
      priority: Number($('#subject-priority').value),
      difficulty: Number($('#subject-difficulty').value),
    });
    event.currentTarget.reset();
    $('#subject-priority').value = '3';
    $('#subject-difficulty').value = '3';
    await refreshAfterChange('Đã thêm môn học.');
  } catch (error) {
    notify(error.message, 'error');
  }
});

$('#availability-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    await api.addAvailability({
      study_date: $('#availability-date').value,
      start_time: $('#availability-start').value,
      end_time: $('#availability-end').value,
    });
    await refreshAfterChange('Đã thêm thời gian rảnh.');
  } catch (error) {
    notify(error.message, 'error');
  }
});

$('#task-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!state.subjects.length) {
    notify('Hãy thêm môn học trước khi tạo Study Task.', 'error');
    return;
  }

  const notes = $('#task-notes').value.trim();
  const link = $('#task-link').value.trim();
  try {
    await api.addTask({
      subject_id: Number($('#task-subject').value),
      title: $('#task-title').value.trim(),
      estimated_hours: Number($('#task-hours').value),
      deadline: $('#task-deadline').value,
      priority: Number($('#task-priority').value),
      difficulty: Number($('#task-difficulty').value),
      notes: notes || null,
      resource_link: link || null,
    });
    event.currentTarget.reset();
    $('#task-hours').value = '2';
    $('#task-priority').value = '3';
    $('#task-difficulty').value = '3';
    renderSubjectSelect();
    await refreshAfterChange('Đã thêm Study Task.');
  } catch (error) {
    notify(error.message, 'error');
  }
});

$('#generate-btn').addEventListener('click', async () => {
  const button = $('#generate-btn');
  button.disabled = true;
  button.innerHTML = '<span class="material-symbols-outlined">sync</span> AI đang tối ưu...';
  try {
    const result = await api.generateSchedule();
    state.aiResult = result;
    state.sessions = result.sessions || [];
    state.dashboard = await api.dashboard();
    renderStats();
    renderAIResult();
    renderTimeline();
    notify(`Đã tạo lịch học. Fitness = ${Number(result.fitness).toFixed(2)}`);
  } catch (error) {
    notify(error.message, 'error');
  } finally {
    button.disabled = false;
    button.innerHTML = '<span class="material-symbols-outlined">auto_fix_high</span> Tạo lịch học bằng AI';
  }
});

$('#availability-list').addEventListener('click', async (event) => {
  const button = event.target.closest('[data-action="delete-availability"]');
  if (!button) return;
  try {
    await api.deleteAvailability(Number(button.dataset.id));
    await refreshAfterChange('Đã xóa thời gian rảnh.');
  } catch (error) {
    notify(error.message, 'error');
  }
});

$('#task-table-body').addEventListener('click', async (event) => {
  const button = event.target.closest('[data-action]');
  if (!button) return;
  const id = Number(button.dataset.id);
  try {
    if (button.dataset.action === 'delete-task') {
      if (!window.confirm('Bạn có chắc muốn xóa công việc này?')) return;
      await api.deleteTask(id);
      await refreshAfterChange('Đã xóa công việc.');
    }
    if (button.dataset.action === 'complete-task') {
      await api.updateTaskStatus(id, 'completed');
      await refreshAfterChange('Đã đánh dấu Task hoàn thành.');
    }
  } catch (error) {
    notify(error.message, 'error');
  }
});

$('#timeline').addEventListener('click', async (event) => {
  const button = event.target.closest('[data-action]');
  if (!button) return;
  const id = Number(button.dataset.id);
  const action = button.dataset.action;

  if (action === 'toggle-session') {
    const detail = document.querySelector(`[data-session-detail="${id}"]`);
    const expanded = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!expanded));
    button.querySelector('.chevron').textContent = expanded ? '+' : '−';
    detail.hidden = expanded;
    return;
  }

  try {
    if (action === 'complete-session') {
      await api.updateSessionStatus(id, 'completed');
      await refreshAfterChange('Đã đánh dấu phiên học hoàn thành.');
    }
    if (action === 'miss-session') {
      await api.updateSessionStatus(id, 'missed');
      await refreshAfterChange('Đã đánh dấu bỏ lỡ. Bấm “Tạo lịch học bằng AI” để lập lại lịch.');
    }
  } catch (error) {
    notify(error.message, 'error');
  }
});

// Gợi ý ngày rảnh mặc định là ngày mai để demo nhanh hơn.
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
$('#availability-date').value = tomorrow.toISOString().slice(0, 10);

loadAll();
