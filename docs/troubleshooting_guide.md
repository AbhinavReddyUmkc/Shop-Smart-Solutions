# Threat Intelligence System: Troubleshooting Guide

## Table of Contents
1. [Common Issues](#common-issues)
2. [Installation Problems](#installation-problems)
3. [Authentication Issues](#authentication-issues)
4. [Performance Problems](#performance-problems)
5. [Data Integration Issues](#data-integration-issues)
6. [API Connectivity Issues](#api-connectivity-issues)
7. [Reporting Problems](#reporting-problems)
8. [UI/UX Issues](#uiux-issues)
9. [System Maintenance](#system-maintenance)
10. [Support Contacts](#support-contacts)

## Common Issues

### System Not Starting

**Symptoms**: Web server returns 503 error, API endpoints unreachable

**Potential Causes**:
- Database connection failure
- Missing environment variables
- Port conflicts
- Insufficient permissions

**Resolution Steps**:

1. Check service status:
   ```bash
   pm2 status
   systemctl status nginx
   ```

2. Verify database connectivity:
   ```bash
   psql -h localhost -U threatuser -d threatdb
   # or
   mongo --host localhost --port 27017
   ```

3. Check environment variables:
   ```bash
   cat .env | grep -v '^#' | grep .
   ```

4. Check logs for errors:
   ```bash
   pm2 logs
   tail -f /var/log/nginx/error.log
   ```

5. Verify port availability:
   ```bash
   netstat -tulpn | grep 3000
   ```

### High CPU/Memory Usage

**Symptoms**: System becomes slow or unresponsive, server resources near 100% utilization

**Potential Causes**:
- Inefficient database queries
- Memory leaks
- Too many concurrent requests
- Background jobs consuming resources

**Resolution Steps**:

1. Identify resource-intensive processes:
   ```bash
   top -c
   htop
   ```

2. Check Node.js memory usage:
   ```bash
   node --inspect
   # Then connect Chrome to chrome://inspect
   ```

3. Analyze database performance:
   ```bash
   EXPLAIN ANALYZE SELECT * FROM threats WHERE severity = 'high';
   ```

4. Enable request logging to identify slow endpoints:
   ```javascript
   app.use((req, res, next) => {
     const start = Date.now();
     res.on('finish', () => {
       const duration = Date.now() - start;
       if (duration > 1000) {
         console.warn(`Slow request: ${req.method} ${req.path} - ${duration}ms`);
       }
     });
     next();
   });
   ```

5. Check for memory leaks:
   ```bash
   node --inspect-brk --expose-gc app.js
   # Use Chrome DevTools Memory tab to take heap snapshots
   ```

### Data Not Updating

**Symptoms**: Dashboard shows stale data, new threats not appearing

**Potential Causes**:
- Cache not invalidated
- Background jobs failing
- Database replication lag
- Permissions issues

**Resolution Steps**:

1. Clear application cache:
   ```bash
   redis-cli FLUSHALL
   ```

2. Check background job status:
   ```bash
   pm2 logs worker
   ```

3. Verify database replication status:
   ```sql
   SELECT * FROM pg_stat_replication;
   ```

4. Check data update logs:
   ```bash
   tail -f /var/log/threat-intel/data-sync.log
   ```

5. Manually trigger data refresh:
   ```bash
   curl -X POST https://your-api.example.com/api/admin/refresh-data
   ```

## Installation Problems

### Database Migration Failures

**Symptoms**: Error during migration, incomplete database schema

**Resolution Steps**:

1. Check migration logs:
   ```bash
   npm run migrate:status
   ```

2. Reset failed migration:
   ```bash
   npm run migrate:rollback
   ```

3. Fix migration files if needed and retry:
   ```bash
   npm run migrate:latest
   ```

4. For severe issues, restore from backup:
   ```bash
   pg_restore -h localhost -U threatuser -d threatdb latest_backup.dump
   ```

### Dependency Installation Errors

**Symptoms**: npm install fails, missing modules errors

**Resolution Steps**:

1. Clear npm cache:
   ```bash
   npm cache clean --force
   ```

2. Remove node_modules and reinstall:
   ```bash
   rm -rf node_modules
   rm package-lock.json
   npm install
   ```

3. Check for Node.js version compatibility:
   ```bash
   node -v # Should match version in .nvmrc
   ```

4. Use specific npm registry if corporate firewall is blocking:
   ```bash
   npm config set registry https://your-registry.example.com
   ```

## Authentication Issues

### Login Failures

**Symptoms**: Users unable to log in, "Invalid credentials" errors

**Resolution Steps**:

1. Verify user exists in database:
   ```sql
   SELECT * FROM users WHERE email = 'user@example.com';
   ```

2. Check if account is locked:
   ```sql
   SELECT * FROM users WHERE email = 'user@example.com' AND locked = true;
   ```

3. Reset user password if needed:
   ```sql
   UPDATE users SET password_hash = '$2a$10$...' WHERE email = 'user@example.com';
   ```

4. Check authentication logs:
   ```bash
   tail -f /var/log/threat-intel/auth.log
   ```

### JWT Token Problems

**Symptoms**: "Invalid token" errors, premature session expiration

**Resolution Steps**:

1. Verify JWT secret is correctly set in environment:
   ```bash
   echo $JWT_SECRET | wc -c # Should be sufficiently long
   ```

2. Check token expiration time:
   ```javascript
   const decodedToken = jwt.decode(token);
   console.log(new Date(decodedToken.exp * 1000));
   ```

3. Ensure server clocks are synchronized:
   ```bash
   timedatectl status
   ```

4. Clear user sessions if needed:
   ```sql
   DELETE FROM sessions WHERE user_id = 123;
   ```

## Performance Problems

### Slow Database Queries

**Symptoms**: API requests timing out, high database CPU usage

**Resolution Steps**:

1. Identify slow queries:
   ```sql
   SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;
   ```

2. Analyze query execution plan:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM threats WHERE source_id = 5;
   ```

3. Add missing indexes:
   ```sql
   CREATE INDEX idx_threats_source_id ON threats(source_id);
   ```

4. Optimize query:
   ```sql
   -- Before
   SELECT * FROM threats WHERE description LIKE '%malware%';
   
   -- After
   SELECT id, name, severity FROM threats WHERE description LIKE '%malware%';
   ```

5. Consider query caching:
   ```javascript
   const cacheKey = `threats:source:${sourceId}`;
   const cachedResult = await redis.get(cacheKey);
   
   if (cachedResult) {
     return JSON.parse(cachedResult);
   }
   
   const result = await db.query('SELECT * FROM threats WHERE source_id = $1', [sourceId]);
   await redis.set(cacheKey, JSON.stringify(result), 'EX', 300); // Cache for 5 minutes
   return result;
   ```

### Slow Frontend Performance

**Symptoms**: UI feels sluggish, high client-side CPU usage

**Resolution Steps**:

1. Optimize bundle size:
   ```bash
   npm run analyze-bundle
   ```

2. Implement code splitting:
   ```javascript
   const Dashboard = React.lazy(() => import('./Dashboard'));
   ```

3. Enable compression:
   ```javascript
   app.use(compression());
   ```

4. Add caching headers:
   ```javascript
   res.setHeader('Cache-Control', 'public, max-age=86400');
   ```

5. Use pagination for large datasets:
   ```javascript
   const { page = 1, limit = 20 } = req.query;
   const offset = (page - 1) * limit;
   
   const threats = await db.query(
     'SELECT * FROM threats ORDER BY created_at DESC LIMIT $1 OFFSET $2',
     [limit, offset]
   );
   ```

## Data Integration Issues

### Feed Import Failures

**Symptoms**: External threat feeds not importing, incomplete data

**Resolution Steps**:

1. Check feed connectivity:
   ```bash
   curl -v https://external-feed.example.com/api/threats
   ```

2. Verify API keys and authentication:
   ```bash
   grep API_KEY .env
   ```

3. Check import logs:
   ```bash
   tail -f /var/log/threat-intel/feed-import.log
   ```

4. Manually trigger feed import:
   ```bash
   node scripts/import-feeds.js --feed=alienvault
   ```

5. Verify data transformation functions:
   ```javascript
   const sampleData = require('./sample-feed-data.json');
   const transformed = transformFeedData(sampleData);
   console.log(transformed);
   ```

### Data Export Problems

**Symptoms**: Unable to export reports or data feeds

**Resolution Steps**:

1. Check export permissions:
   ```sql
   SELECT can_export FROM user_permissions WHERE user_id = 123;
   ```

2. Verify export directory is writable:
   ```bash
   touch /path/to/exports/test.txt
   ```

3. Check export logs:
   ```bash
   tail -f /var/log/threat-intel/exports.log
   ```

4. Test export functionality manually:
   ```javascript
   const exportService = require('./services/export');
   exportService.exportToCSV(threatId, '/tmp/test-export.csv')
     .then(() => console.log('Export successful'))
     .catch(err => console.error('Export failed:', err));
   ```

## API Connectivity Issues

### API Timeouts

**Symptoms**: Requests to API timing out, connection refused errors

**Resolution Steps**:

1. Check API server status:
   ```bash
   pm2 status api-server
   ```

2. Verify network connectivity:
   ```bash
   curl -v http://localhost:3000/api/health
   ```

3. Check for firewall issues:
   ```bash
   iptables -L
   ```

4. Increase timeout settings if needed:
   ```javascript
   // Client-side
   axios.defaults.timeout = 30000; // 30 seconds
   
   // Server-side
   server.timeout = 60000; // 60 seconds
   ```

5. Check server logs for errors:
   ```bash
   pm2 logs api-server
   ```

### CORS Issues

**Symptoms**: Browser console shows CORS errors, API requests failing

**Resolution Steps**:

1. Check CORS configuration:
   ```javascript
   app.use(cors({
     origin: process.env.ALLOWED_ORIGINS.split(','),
     methods: ['GET', 'POST', 'PUT', 'DELETE'],
     allowedHeaders: ['Content-Type', 'Authorization']
   }));
   ```

2. Verify the request origin is allowed:
   ```bash
   grep ALLOWED_ORIGINS .env
   ```

3. Add missing origins if needed:
   ```bash
   echo "ALLOWED_ORIGINS=https://app.example.com,https://admin.example.com" >> .env
   ```

4. Restart the API server:
   ```bash
   pm2 restart api-server
   ```

## Reporting Problems

### Report Generation Failures

**Symptoms**: Unable to generate PDF/CSV reports, timeout during generation

**Resolution Steps**:

1. Check temp directory permissions:
   ```bash
   ls -la /tmp
   ```

2. Verify PDF generation dependencies:
   ```bash
   which wkhtmltopdf
   ```

3. Check report generation logs:
   ```bash
   tail -f /var/log/threat-intel/reports.log
   ```

4. Test report generation with smaller dataset:
   ```javascript
   const reportService = require('./services/reports');
   reportService.generatePDF({ limit: 10 }, '/tmp/test.pdf')
     .then(() => console.log('Report generated successfully'))
     .catch(err => console.error('Report generation failed:', err));
   ```

5. Increase memory allocation if needed:
   ```bash
   NODE_OPTIONS=--max-old-space-size=4096 node scripts/generate-report.js
   ```

### Missing or Incomplete Data in Reports

**Symptoms**: Reports missing expected data or showing incomplete information

**Resolution Steps**:

1. Verify data exists in database:
   ```sql
   SELECT COUNT(*) FROM threats WHERE severity = 'high';
   ```

2. Check report template integrity:
   ```bash
   cat templates/pdf-report.hbs
   ```

3. Test data transformation functions:
   ```javascript
   const data = await threatService.getThreatsForReport(filters);
   console.log(JSON.stringify(data, null, 2));
   ```

4. Verify permissions for report data:
   ```sql
   SELECT * FROM report_permissions WHERE user_id = 123;
   ```

## UI/UX Issues

### Rendering Problems

**Symptoms**: UI elements missing or incorrectly displayed

**Resolution Steps**:

1. Check browser console for errors:
   ```javascript
   // In browser console
   console.log('Debugging UI issues');
   ```

2. Verify CSS is loading correctly:
   ```bash
   curl -I https://app.example.com/styles.css
   ```

3. Test with different browsers:
   ```bash
   # Run tests in multiple browsers
   npm run test:browsers
   ```

4. Clear browser cache:
   ```javascript
   // In browser console
   location.reload(true);
   ```

5. Check for JavaScript errors:
   ```bash
   grep -r "console.error" src/
   ```

### Browser Compatibility Issues

**Symptoms**: Features working in some browsers but not others

**Resolution Steps**:

1. Check browser versions:
   ```javascript
   // In browser console
   navigator.userAgent
   ```

2. Verify polyfills are loaded:
   ```html
   <script src="https://cdn.polyfill.io/v3/polyfill.min.js"></script>
   ```

3. Test with BrowserStack:
   ```bash
   npm run test:browserstack
   ```

4. Add browser-specific CSS fixes:
   ```css
   @supports (-webkit-appearance:none) {
     /* Safari-specific fixes */
   }
   ```

## System Maintenance

### Backup and Restore

**Database Backup**:
```bash
# PostgreSQL
pg_dump -h localhost -U threatuser -d threatdb -F c -f backup_$(date +%Y%m%d).dump

# MongoDB
mongodump --host localhost --db threatdb --out backup_$(date +%Y%m%d)
```

**Database Restore**:
```bash
# PostgreSQL
pg_restore -h localhost -U threatuser -d threatdb backup_20250410.dump

# MongoDB
mongorestore --host localhost --db threatdb backup_20250410/threatdb
```

### Log Rotation

**Setup Log Rotation**:
```
# /etc/logrotate.d/threat-intel
/var/log/threat-intel/*.log {
  daily
  missingok
  rotate 14
  compress
  delaycompress
  notifempty
  create 0640 threatuser threatuser
  sharedscripts
  postrotate
    systemctl reload rsyslog
  endscript
}
```

### Cache Management

**Clear Redis Cache**:
```bash
redis-cli FLUSHALL
```

**Selective Cache Clearing**:
```bash
redis-cli KEYS "threat:*" | xargs redis-cli DEL
```

### Server Updates

**Update System Packages**:
```bash
apt update
apt upgrade -y
```

**Update Node.js Dependencies**:
```bash
npm outdated
npm update
```

**Security Updates Only**:
```bash
apt update
apt upgrade -y --only-upgrade --security
```

## Support Contacts

### Technical Support Team

- **Email**: support@threatintel.example.com
- **Phone**: +1-800-555-0123
- **Hours**: 24/7 for critical issues, 8am-6pm ET for standard support

### Emergency Escalation Process

1. Contact on-call engineer: +1-800-555-0199
2. If no response within 15 minutes, email escalation@threatintel.example.com
3. For critical production issues, contact the CTO directly at cto@threatintel.example.com

### Reporting Security Vulnerabilities

- **Email**: security@threatintel.example.com
- **Secure Form**: https://threatintel.example.com/security/report
- **Bug Bounty Program**: https://hackerone.com/threatintel

### Documentation and Resources

- **Knowledge Base**: https://support.threatintel.example.com/kb
- **API Documentation**: https://api.threatintel.example.com/docs
- **GitHub Repository**: https://github.com/example/threat-intel
- **Community Forum**: https://community.threatintel.example.com