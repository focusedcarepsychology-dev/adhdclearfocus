# ADHDclearfocus v2 Reconciled Package

This package keeps the improved v2 structure and API/security fixes, while adding/replacing the useful files from the latest upload batch.

## Added or replaced from latest uploaded files
- resources.html — replaced with the richer uploaded resource/research page.
- strategies.html — replaced with the richer uploaded strategy library.
- thank-you.html — replaced with the richer post-payment page.
- workplace.html — replaced with the richer employer/workplace page.
- sw.js — replaced with the newer service worker.
- welcome.html — added; this was not in the previous v2 package.
- UPLOAD_INSTRUCTIONS.txt — added for deployment reference.

## Kept from v2 package because safer/newer
- vercel.json — kept the stronger v2 version with API rewrites, security headers and caching. The uploaded vercel.json was minimal.
- robots.txt — used the expanded uploaded bot rules but corrected the sitemap from .com to .ie.
- requirements.txt — kept the correct one-line reportlab dependency. Some uploaded requirements files contained webhook Python code and were misnamed.
- API files under /api — kept the correctly named v2 versions. Several latest uploads were shifted/misnamed, e.g. auth(2).py contained requirements content, generate_report(2).py contained checkout code, and download(1) contained the report generator.

## Do not upload the loose misnamed files directly
Use this reconciled folder/zip instead, because several of the loose upload files have correct content but wrong filenames. Uploading them as-is would break Vercel functions.
