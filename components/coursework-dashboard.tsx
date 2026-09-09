'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';

type Subject = {
  id: string;
  name: string;
  description?: string | null;
  resource_count?: number;
};

type Resource = {
  id: string;
  title: string;
  description?: string | null;
  type: string;
  status: 'pending' | 'processing' | 'ready' | 'failed';
  subject_id: string;
  created_at: string;
};

type CreateResourceResult = Resource & { upload_url?: string; upload_id?: string };

type ApiEnvelope<T> = { data: T; error: null } | { data: null; error: { code: string; message: string } };

const resourceTypes = ['practical', 'note', 'book', 'guideline', 'assignment', 'reference', 'other'];

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, { ...options, headers: { 'Content-Type': 'application/json', ...options?.headers } });
  const body = (await response.json()) as ApiEnvelope<T>;
  if (!response.ok || body.error) throw new Error(body.error?.message ?? 'The request could not be completed.');
  return body.data;
}

function statusLabel(status: Resource['status']) {
  return status === 'processing' ? 'Processing' : status[0].toUpperCase() + status.slice(1);
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value));
}

export function CourseworkDashboard() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showSubjectForm, setShowSubjectForm] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [subjectName, setSubjectName] = useState('');
  const [subjectDescription, setSubjectDescription] = useState('');
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadType, setUploadType] = useState('practical');
  const [uploadSubject, setUploadSubject] = useState('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  async function loadLibrary() {
    setLoading(true);
    setError('');
    try {
      const [subjectData, resourceData] = await Promise.all([
        request<Subject[]>('/api/subjects'),
        request<Resource[]>('/api/resources'),
      ]);
      setSubjects(subjectData);
      setResources(resourceData);
      setUploadSubject((current) => current || subjectData[0]?.id || '');
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load your library.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void loadLibrary(); }, []);

  const visibleResources = useMemo(() => resources.filter((resource) => {
    const matchesSubject = selectedSubject === 'all' || resource.subject_id === selectedSubject;
    const searchText = `${resource.title} ${resource.description ?? ''} ${resource.type}`.toLowerCase();
    return matchesSubject && searchText.includes(query.toLowerCase());
  }), [query, resources, selectedSubject]);

  async function createSubject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!subjectName.trim()) return;
    setSaving(true);
    setError('');
    try {
      const subject = await request<Subject>('/api/subjects', {
        method: 'POST',
        body: JSON.stringify({ name: subjectName.trim(), description: subjectDescription.trim() || null }),
      });
      setSubjects((current) => [...current, subject]);
      setSelectedSubject(subject.id);
      setUploadSubject(subject.id);
      setSubjectName('');
      setSubjectDescription('');
      setShowSubjectForm(false);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : 'Unable to create the subject.');
    } finally {
      setSaving(false);
    }
  }

  async function uploadResource(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!uploadTitle.trim() || !uploadSubject || !uploadFile) return;
    setSaving(true);
    setUploadProgress(20);
    setError('');
    try {
      const resourceResult = await request<CreateResourceResult>('/api/resources', {
        method: 'POST',
        body: JSON.stringify({ title: uploadTitle.trim(), type: uploadType, subject_id: uploadSubject, file_name: uploadFile.name, mime_type: uploadFile.type, size_bytes: uploadFile.size }),
      });
      if (resourceResult.upload_url) {
        const uploadResponse = await fetch(resourceResult.upload_url, { method: 'PUT', body: uploadFile, headers: { 'Content-Type': uploadFile.type || 'application/octet-stream' } });
        if (!uploadResponse.ok) throw new Error('The file could not be uploaded.');
        setUploadProgress(80);
        await request(`/api/resources/${resourceResult.id}/files/complete`, {
          method: 'POST',
          body: JSON.stringify({ upload_id: resourceResult.upload_id, file_name: uploadFile.name, mime_type: uploadFile.type, size_bytes: uploadFile.size }),
        });
      }
      setUploadProgress(100);
      setResources((current) => [resourceResult, ...current]);
      setUploadTitle('');
      setUploadFile(null);
      setShowUploadForm(false);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : 'Upload failed. Please try again.');
    } finally {
      setSaving(false);
      window.setTimeout(() => setUploadProgress(0), 500);
    }
  }

  const subjectNameFor = (id: string) => subjects.find((subject) => subject.id === id)?.name ?? 'Unassigned';

  return (
    <main className="dashboard-shell">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-kicker">COURSEWORK LIBRARY / 2026</p>
          <h1>Keep the work<br /><em>close at hand.</em></h1>
          <p className="dashboard-lede">Your private shelf for practicals, notes, and the little discoveries between them.</p>
        </div>
        <div className="header-actions">
          <span className="sync-status"><span className="status-dot" /> Synced just now</span>
          <button className="button button-dark" type="button" onClick={() => setShowUploadForm(true)}>+ Upload resource</button>
        </div>
      </header>

      {error && <div className="alert" role="alert"><strong>Something needs attention.</strong> {error}<button type="button" onClick={() => setError('')}>Dismiss</button></div>}

      <section className="library-summary" aria-label="Library overview">
        <div><span className="summary-label">All resources</span><strong>{resources.length.toString().padStart(2, '0')}</strong></div>
        <div><span className="summary-label">Study areas</span><strong>{subjects.length.toString().padStart(2, '0')}</strong></div>
        <div><span className="summary-label">Ready to view</span><strong>{resources.filter((resource) => resource.status === 'ready').length.toString().padStart(2, '0')}</strong></div>
      </section>

      <section className="workspace-grid">
        <aside className="subjects-panel" aria-labelledby="subjects-heading">
          <div className="panel-heading"><div><p className="dashboard-kicker">ORGANIZE</p><h2 id="subjects-heading">Study areas</h2></div><button className="icon-button" type="button" aria-label="Add study area" onClick={() => setShowSubjectForm(true)}>+</button></div>
          <button className={`subject-row ${selectedSubject === 'all' ? 'is-selected' : ''}`} type="button" onClick={() => setSelectedSubject('all')}><span className="subject-mark all-mark">A</span><span><strong>Everything</strong><small>{resources.length} resources</small></span></button>
          {subjects.map((subject) => <button className={`subject-row ${selectedSubject === subject.id ? 'is-selected' : ''}`} type="button" key={subject.id} onClick={() => setSelectedSubject(subject.id)}><span className="subject-mark">{subject.name.slice(0, 1).toUpperCase()}</span><span><strong>{subject.name}</strong><small>{resources.filter((resource) => resource.subject_id === subject.id).length} resources</small></span></button>)}
          {!loading && subjects.length === 0 && <p className="empty-copy">No study areas yet. Start with one for a course or semester.</p>}
        </aside>

        <section className="resources-panel" aria-labelledby="resources-heading">
          <div className="panel-heading resources-heading"><div><p className="dashboard-kicker">YOUR SHELF</p><h2 id="resources-heading">{selectedSubject === 'all' ? 'Recent resources' : subjectNameFor(selectedSubject)}</h2></div><span className="resource-count">{visibleResources.length} shown</span></div>
          <label className="search-field"><span aria-hidden="true">/</span><input type="search" placeholder="Search title, type, or description" value={query} onChange={(event) => setQuery(event.target.value)} /><kbd>⌘ K</kbd></label>
          {loading && <div className="state-panel"><span className="loader" />Loading your library...</div>}
          {!loading && visibleResources.length === 0 && <div className="state-panel empty-state"><span className="empty-icon">+</span><h3>{query ? 'Nothing matches that search.' : 'Your shelf is ready for its first upload.'}</h3><p>{query ? 'Try a different title, type, or study area.' : 'Add a file and it will appear here with its processing status.'}</p><button className="button button-dark" type="button" onClick={() => setShowUploadForm(true)}>Upload a resource</button></div>}
          <div className="resource-list">{visibleResources.map((resource) => <article className="resource-item" key={resource.id}><div className="file-badge">{resource.type.slice(0, 3).toUpperCase()}</div><div className="resource-body"><div className="resource-title-line"><h3>{resource.title}</h3><span className={`resource-status status-${resource.status}`}><span />{statusLabel(resource.status)}</span></div><p>{subjectNameFor(resource.subject_id)} <span className="muted-separator">/</span> {resource.type} <span className="muted-separator">/</span> {formatDate(resource.created_at)}</p></div><a className="resource-link" href={`/resources/${resource.id}`} aria-label={`Open ${resource.title}`}>Open <span>↗</span></a></article>)}</div>
        </section>
      </section>

      {showSubjectForm && <div className="modal-backdrop" role="presentation"><form className="modal" onSubmit={createSubject}><button className="modal-close" type="button" aria-label="Close" onClick={() => setShowSubjectForm(false)}>×</button><p className="dashboard-kicker">NEW STUDY AREA</p><h2>Give this work a home.</h2><label>Name<input autoFocus value={subjectName} onChange={(event) => setSubjectName(event.target.value)} placeholder="e.g. Digital Image Processing" required /></label><label>Description <span>(optional)</span><textarea value={subjectDescription} onChange={(event) => setSubjectDescription(event.target.value)} placeholder="What belongs here?" rows={3} /></label><div className="modal-actions"><button className="button" type="button" onClick={() => setShowSubjectForm(false)}>Cancel</button><button className="button button-dark" type="submit" disabled={saving}>{saving ? 'Creating...' : 'Create study area'}</button></div></form></div>}
      {showUploadForm && <div className="modal-backdrop" role="presentation"><form className="modal" onSubmit={uploadResource}><button className="modal-close" type="button" aria-label="Close" onClick={() => setShowUploadForm(false)}>×</button><p className="dashboard-kicker">ADD TO SHELF</p><h2>Upload a resource.</h2><label>File<input type="file" onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)} required /></label><label>Title<input autoFocus value={uploadTitle} onChange={(event) => setUploadTitle(event.target.value)} placeholder="e.g. Practical 04: Image segmentation" required /></label><div className="form-row"><label>Study area<select value={uploadSubject} onChange={(event) => setUploadSubject(event.target.value)} required><option value="" disabled>Select one</option>{subjects.map((subject) => <option value={subject.id} key={subject.id}>{subject.name}</option>)}</select></label><label>Type<select value={uploadType} onChange={(event) => setUploadType(event.target.value)}>{resourceTypes.map((type) => <option value={type} key={type}>{type}</option>)}</select></label></div>{uploadProgress > 0 && <div className="progress-track"><span style={{ width: `${uploadProgress}%` }} /></div>}<div className="modal-actions"><button className="button" type="button" onClick={() => setShowUploadForm(false)}>Cancel</button><button className="button button-dark" type="submit" disabled={saving || subjects.length === 0}>{saving ? 'Uploading...' : 'Add resource'}</button></div></form></div>}
    </main>
  );
}
