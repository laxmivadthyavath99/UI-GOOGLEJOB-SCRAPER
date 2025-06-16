import React, { useState } from 'react';

function App() {
  const [jobTitle, setJobTitle] = useState('');
  const [location, setLocation] = useState('');
  const [experience, setExperience] = useState('');
  const [jobType, setJobType] = useState('');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 5;

  const handleSearch = async (newPage = 1) => {
    setLoading(true);
    setError('');
    setJobs([]);
    const queryParts = [jobTitle, location, experience, jobType].filter(Boolean);
    const searchQuery = queryParts.join('+').replace(/\s+/g, '+');
    try {
      const response = await fetch('http://127.0.0.1:5000/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: searchQuery, page: newPage, page_size: pageSize }),
      });
      if (!response.ok) throw new Error('Failed to fetch job info');
      const data = await response.json();
      setJobs(data.jobs);
      setTotal(data.total);
      setPage(newPage);
    } catch (err) {
      setError('Failed to fetch job info. Please check inputs and try again.');
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Google Job Info Scraper</h2>
      <div style={{ marginBottom: 10 }}>
        <input
          value={jobTitle}
          onChange={e => setJobTitle(e.target.value)}
          placeholder="Job Title"
          style={{ marginRight: 10 }}
        />
        <input
          value={location}
          onChange={e => setLocation(e.target.value)}
          placeholder="Location"
          style={{ marginRight: 10 }}
        />
        <input
          value={experience}
          onChange={e => setExperience(e.target.value)}
          placeholder="Experience (e.g. 2 years)"
          style={{ marginRight: 10 }}
        />
        <input
          value={jobType}
          onChange={e => setJobType(e.target.value)}
          placeholder="Job Type (e.g. full time)"
          style={{ marginRight: 10 }}
        />
        <button onClick={() => handleSearch(1)} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {error && <div style={{ color: 'red' }}>{error}</div>}

      <div style={{ marginTop: 30 }}>
        {Array.isArray(jobs) && jobs.length > 0 && (
          <>
            <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse', width: '100%' }}>
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Company Name</th>
                  <th>Location</th>
                  <th>Posted Date</th>
                  <th>Job Description</th>
                  <th>Phone Number</th>
                  <th>Email Address</th>
                  <th>Apply Links</th>
                  <th>Job Link</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job, idx) => (
                  <tr key={idx}>
                    <td>{job['Job Title']}</td>
                    <td>{job['Company Name']}</td>
                    <td>{job['Location']}</td>
                    <td>{job['Posted Date']}</td>
                    <td style={{ maxWidth: 300, wordBreak: 'break-word' }}>{job['Job Description']}</td>
                    <td>{job['Phone Number']}</td>
                    <td>{job['Email Address']}</td>
                    <td>
                      {job['Apply Links'] && (
                        <ul>
                          {Object.entries(JSON.parse(job['Apply Links'])).map(([text, link], i) => (
                            <li key={i}><a href={link} target="_blank" rel="noopener noreferrer">{text}</a></li>
                          ))}
                        </ul>
                      )}
                    </td>
                    <td>
                      <a href={job['Job Link']} target="_blank" rel="noopener noreferrer">View</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ marginTop: 20 }}>
              <button onClick={() => handleSearch(page - 1)} disabled={page === 1}>Prev</button>
              <span style={{ margin: '0 10px' }}>Page {page}</span>
              <button onClick={() => handleSearch(page + 1)} disabled={page * pageSize >= total}>Next</button>
              <span style={{ marginLeft: 10 }}>Total Jobs: {total}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
