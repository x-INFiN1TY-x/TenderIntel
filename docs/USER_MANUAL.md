# TenderIntel User Manual

**Version:** 1.0.0  
**Last Updated:** October 22, 2025  
**For:** Business Analysts, Procurement Specialists, Competitive Intelligence Teams

## **📖 Table of Contents**

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Intelligent Search](#intelligent-search)
4. [Advanced Filtering](#advanced-filtering)
5. [Competitive Intelligence](#competitive-intelligence)
6. [Executive Dashboards](#executive-dashboards)
7. [Data Export](#data-export)
8. [Troubleshooting](#troubleshooting)

---

## **🎯 Introduction**

TenderIntel is an AI-powered platform that helps you find and analyze government procurement opportunities in India. It solves critical problems with traditional portal searches:

**What TenderIntel Does:**
- 🔍 **Intelligent Search:** Expands technical acronyms (e.g., "LAN" → "Local Area Network", "Layer 2 Switch", etc.)
- 🎯 **Zero False Positives:** Prevents "LAN" from matching irrelevant "land development" tenders
- 📊 **Competitive Intelligence:** Track which firms are winning in your market
- 💰 **Market Analysis:** Understand pricing, deal sizes, and competitive intensity
- 📈 **Executive Dashboards:** Visualize market trends and opportunities

---

## **🚀 Getting Started**

### **Accessing TenderIntel**

**Web Interface:** Open `http://localhost:8080` in your browser  
**API Documentation:** Visit `http://localhost:8002/docs` for interactive API  
**Quick Test:** `curl "http://localhost:8002/search?q=cloud"`

### **First Search**

1. Open web interface
2. Click on **"Search"** in navigation
3. Enter keyword (try: "cloud", "api", "networking", "security")
4. Press **Enter** or click **"Search"** button
5. View results with similarity percentages

**Example:** Search for "lan" finds:
- ✅ "VLAN configuration and Ethernet switching equipment..." (100% match)
- ✅ "Supply and installation of Layer 2 switches..." (85% match)
- ✅ "Procurement of local area network infrastructure..." (84% match)

---

## **🔍 Intelligent Search**

### **How Intelligent Search Works**

TenderIntel transforms your simple keywords into comprehensive searches:

**Example Search: "api"**

**What You Type:** `api`

**What TenderIntel Searches:**
- "application programming interface"
- "rest api"
- "api gateway"
- "openapi"

**Result:** Finds all API-related tenders with relevance scoring

### **Keyword Expansion**

**266+ Technical Keywords Supported:**
- **Networking:** lan, wan, vpn, dns, dhcp, vlan, mpls, sdwan, sdn, noc, nms
- **Cloud:** api, rest, soap, graphql, webhook, load, cdn, proxy
- **Security:** iam, pam, mfa, sso, saml, oauth, ldap, siem, soar, soc, firewall, waf
- **Database:** db, sql, nosql, mysql, postgresql, oracle, mongodb, redis
- **AI/ML:** ai, ml, nlp, cv, genai, llm, chatgpt, transformer
- **Government:** rfp, rfq, tender, bid, aoc, gem, cppp, nic, cdac

**Test Keyword Expansion:**
1. Click **"🔍 Search"** page
2. Type keyword
3. Toggle **"Show Expansions"** button (lightning icon)
4. See expanded phrases displayed as chips

### **Search Best Practices**

**DO:**
- ✅ Use technical acronyms (e.g., "lan", "api", "iam")
- ✅ Search single concepts (e.g., "cloud" not "cloud security networking")
- ✅ Try shorter terms first (e.g., "api" before "application programming interface")
- ✅ Use filters to narrow results

**DON'T:**
- ❌ Type long phrases (the system does this for you)
- ❌ Use multiple unrelated keywords in one search
- ❌ Add wildcards or special characters (*, ?, @)

---

## **🎛️ Advanced Filtering**

### **8 Filter Categories Available:**

#### **1. Service Categories**
Filter by IT service type:
- Cloud Services
- Networking
- Database Services
- Security Solutions
- Software & Applications
- Integration Services
- Hardware & Equipment

#### **2. Organizations**
Filter by issuing agency (searchable):
- National Informatics Centre (NIC)
- Ministry of Electronics and IT (MeitY)
- C-DAC
- CERT-In
- And 40+ more government organizations

#### **3. Value Ranges**
Filter by deal size:
- Up to ₹10 Lakh
- ₹10L - ₹1 Crore
- ₹1Cr - ₹5 Crore
- ₹5Cr - ₹10 Crore
- ₹10 Crore+

#### **4. Geographic Regions**
Filter by location:
- Northern India
- Southern India
- Eastern India
- Western India
- Central India

#### **5. Tender Status**
Filter by procurement stage:
- Published AOC (contract awarded)
- Live Tender (bidding open)
- Closed

#### **6. Department Type**
- Central Government
- State Government

#### **7. Complexity Level**
- Simple (routine procurement)
- Moderate (standard projects)
- Complex (large-scale implementations)

#### **8. Date Range**
- From Date (AOC date filter)
- To Date (AOC date filter)

#### **9. Match Quality**
Similarity threshold slider (0-100%):
- **0%:** Show all results
- **50%:** Moderate matches only
- **100%:** Exact matches only

### **Using Filters:**

1. Click **"Advanced Filters"** header to expand
2. Select desired filter options (checkboxes, dropdowns, dates)
3. Click **"Apply Filters"** button
4. See filtered results with active filter count badge
5. Click **"Clear All Filters"** to reset

**Example:** Find cloud tenders in Delhi over ₹1 Crore:
- Keyword: "cloud"
- Service Categories: ✓ Cloud Services
- Regions: ✓ Northern India (Delhi)
- Value Ranges: ✓ ₹1Cr - ₹5Cr, ✓ ₹5Cr+

---

## **📊 Competitive Intelligence**

### **Market Analysis**

**Navigate to:** Dashboard → Intelligence → Competitive Analysis

**Available Intelligence:**
- **Service Category Breakdown:** Tender counts by IT category
- **Top Organizations:** Most active government agencies
- **Regional Distribution:** Geographic procurement patterns
- **Complexity Analysis:** Simple vs moderate vs complex tenders
- **Firm Win Tracking:** Which competitors are winning

### **Firm Scorecards**

**Access Firm Analysis:**
1. Go to **"Analytics"** page
2. Search for firm name (e.g., "TCS", "Infosys", "Wipro")
3. View comprehensive scorecard:
   - Portfolio value and contract count
   - Market share percentage
   - Average deal size
   - Award velocity (wins per quarter)
   - Competitive position
   - Risk assessment

### **Market Share Analysis**

**Understand Market Structure:**
- **HHI Index:** Market concentration measure (0-1 scale)
  - < 0.10: Highly competitive
  - 0.10-0.15: Competitive
  - 0.15-0.25: Moderately concentrated
  - > 0.25: Highly concentrated

**Example:** Cloud services market:
- Total Market Value: ₹127.4 Cr
- Active Competitors: 18 firms
- HHI Index: 0.067 (competitive)
- Top 3 Share: 68.9%

---

## **📈 Executive Dashboards**

### **Dashboard Overview**

**Navigate to:** Dashboard (home page)

**Key Metrics Displayed:**
- **Total Market Value:** Cumulative tender value tracked
- **Active Competitors:** Number of firms detected
- **Market Concentration:** HHI index for competitive analysis
- **Average Deal Size:** Mean contract value

### **Interactive Visualizations**

#### **1. Market Trends Chart**
- Line/bar chart showing market growth over time
- Toggle between different time periods
- Export data as CSV

#### **2. Service Distribution**
- Doughnut chart showing tender distribution by category
- Click to drill down into specific services
- View detailed statistics table

#### **3. Top Performers**
- Ranked list of firms by various metrics:
  - Contract count
  - Total value
  - Market share
  - Growth rate
- Click firm to view detailed scorecard

#### **4. Recent Activity**
- Live feed of new tenders and updates
- Filter by service category or region
- Export activity log

---

## **🎯 Service×Firm Heatmap (Intelligence Page)**

### **Understanding the Heatmap**

**Navigate to:** Intelligence page

**What It Shows:**
- 7 Service Categories (rows)
- 37+ Active Firms (columns)
- Color-coded performance indicators:
  - 🟢 Dark Green: High performance (>80%)
  - 🟡 Yellow: Medium performance (40-80%)
  - 🔴 Red: Low performance (<40%)
  - ⚪ Gray: No activity

### **Using the Heatmap:**

1. **Switch Metrics:** Dropdown selector
   - Market Share % (default)
   - Contract Count
   - Total Value (₹)
   
2. **Interactive Features:**
   - Hover over cells for detailed tooltips
   - Click cells to drill down into specifics
   - Export entire matrix as CSV

3. **Insights:**
   - Identify competitor strengths by service
   - Spot market opportunities (white spaces)
   - Track competitive positioning changes

---

## **📊 Data Export**

### **Export Search Results**

**From Search Page:**
1. Perform search with desired filters
2. Select specific results (checkboxes) OR export all
3. Click **"📊 Export CSV"** button
4. File downloads with format: `search_results_timestamp.csv`

**Export Contains:**
- Tender ID, Title, Organization, Status
- AOC Date, Service Category, Region
- Similarity %, URL

### **Export Dashboard Data**

**From Dashboard:**
1. Click user menu (top right)
2. Select **"📄 Export Report"**
3. Generates executive summary CSV with:
   - KPI metrics
   - Service breakdown
   - Top performers
   - Market intelligence

### **Bulk Export Options**

**Available Formats:**
- **CSV:** For Excel/Google Sheets analysis
- **JSON:** For programmatic processing
- **Excel:** (Requires additional library)

---

## **💡 Use Case Examples**

### **Use Case 1: Competitive Tracking**

**Scenario:** Track TCS wins in cloud services

**Steps:**
1. Search: "cloud"
2. Filters: Service Categories → Cloud Services
3. Sort by: AOC Date (newest first)
4. Look for: Organization mentions "TCS" or "Tata Consultancy"
5. Export results for analysis

### **Use Case 2: Opportunity Identification**

**Scenario:** Find networking tenders in Delhi

**Steps:**
1. Search: "networking" or "lan"
2. Filters:
   - Regions → Northern India
   - Value Ranges → ₹1Cr+
   - Status → Live Tender
3. Review results and bid timelines
4. Save search for daily monitoring

### **Use Case 3: Market Intelligence**

**Scenario:** Understand security services market

**Steps:**
1. Navigate to: Intelligence → Heatmap
2. Look at: Security row across all firms
3. Identify: Market leaders and gaps
4. Click to: Dashboard for detailed metrics
5. Export: Full market analysis report

### **Use Case 4: Pricing Benchmarks**

**Scenario:** Benchmark a ₹5 Cr cloud deal

**Steps:**
1. Navigate to: Analytics page
2. Enter: Deal Value ₹50,000,000
3. Select: Service Category: Cloud
4. View: Percentile ranking (e.g., 65th percentile)
5. See: Market comparisons and recommendations

---

## **⚙️ User Preferences**

### **Customizing Your Experience**

**Access Settings:**
1. Click user avatar (top right)
2. Select **"⚙️ Preferences"**

**Available Settings:**
- **Default Page:** Dashboard, Search, Intelligence, or Analytics
- **Auto-Refresh Interval:** 30s, 1min, 5min, or Manual
- **Display Density:** Compact, Comfortable, or Spacious
- **Theme:** (Future: Light/Dark mode)

### **Saved Searches**

**Save Current Search:**
1. Perform search with desired filters
2. Click **"Save Search"** button
3. Name your search (auto-named if you skip)
4. Access later from **"History & Saved"** sidebar

**Manage Saved Searches:**
- Load: Click search name
- Delete: Click trash icon
- Limit: 20 saved searches maximum

### **Search History**

- Automatic tracking of last 10 searches
- Shows: Query, result count, timestamp
- Click to re-run search
- Clear all from History & Saved panel

---

## **🔍 Advanced Search Tips**

### **Synonym System Tips**

**Best Keywords for Government Procurement:**
- **Generic IT:** api, cloud, database, network, security
- **Procurement:** rfp, rfq, tender, bid, aoc, gem, cppp
- **Specific:** lan, vpn, firewall, erp, crm, iot
- **Agencies:** nic, cdac, meity, cert_in

**How Expansions Help:**
- "api" expands to 4 phrases → finds 10x more tenders
- "lan" with anti-patterns → avoids "land development" false positives
- Domain detection → "lan" classified as "networking" (95% confidence)

### **Combining Search + Filters**

**Strategy:** Start broad, narrow with filters

**Example Workflow:**
1. **Broad Search:** "security" (finds 20+ tenders)
2. **Add Service Filter:** Security Solutions (narrows to 12)
3. **Add Region:** Northern India (narrows to 5)
4. **Add Value:** ₹1Cr+ (narrows to 2 relevant opportunities)

### **Understanding Match Percentages**

**Similarity Score Explained:**
- **90-100%:** Multiple exact phrase matches (high relevance)
- **70-89%:** Some phrase matches with BM25 ranking
- **50-69%:** Related terms with moderate relevance
- **<50%:** Weak matches (use filters to improve)

**BM25 Algorithm:**
- Industry-standard relevance scoring
- Considers: term frequency, document length, phrase proximity
- Same algorithm used by: Elasticsearch, Lucene, Google

---

## **🎯 Workflow Best Practices**

### **Daily Monitoring Workflow**

**Morning Routine (15 minutes):**
1. Open Dashboard → Check new tenders count
2. Review Recent Activity feed
3. Check saved search alerts
4. Scan heatmap for competitor activity changes

### **Opportunity Analysis Workflow**

**When New Tender Found (30 minutes):**
1. Review tender details (title, organization, value, dates)
2. Check Service×Firm heatmap for competitor positioning
3. Analyze market context (HHI, average deal size)
4. Review firm scorecards for potential competitors
5. Export tender details for proposal preparation

### **Market Research Workflow**

**Monthly Market Analysis (1-2 hours):**
1. Dashboard → Executive Summary (market overview)
2. Intelligence → Competitive Analysis (firm activity)
3. Analytics → Market Analysis (HHI, trends, growth)
4. Heatmap → Identify white spaces and opportunities
5. Export comprehensive report for stakeholders

---

## **📱 Mobile Access**

TenderIntel is mobile-responsive:

**Mobile Features:**
- Simplified navigation for thumb access
- Card-based results (easier on mobile)
- Touch-optimized filters
- Swipe gestures for pagination

**Mobile Tips:**
- Use landscape mode for heatmap visualization
- Save common searches for quick access
- Export directly from mobile interface

---

## **⚡ Performance Tips**

### **Fast Searches:**
- Use short keywords (1-2 words)
- Let expansion system do the work
- Apply filters after initial search
- Limit results to 25-50 for faster loading

### **Cache Management:**
- Data cached for 2-5 minutes
- Clear cache if seeing stale data: User Menu → Clear Cache
- Auto-refresh available in preferences

---

## **🆘 Troubleshooting**

### **No Results Found**

**Problem:** Search returns zero results

**Solutions:**
1. **Remove Filters:** Too restrictive filtering
2. **Broader Keywords:** Try related terms
3. **Check Spelling:** Verify keyword spelling
4. **Try Expansions:** Enable expansion display to see what's being searched

### **Slow Performance**

**Problem:** Searches taking >5 seconds

**Solutions:**
1. **Reduce Result Limit:** Set to 25 instead of 100
2. **Simplify Filters:** Use fewer filter categories
3. **Check Network:** Verify backend connectivity
4. **Clear Cache:** User Menu → Clear Cache

### **Backend Not Responding**

**Problem:** "Cannot reach backend" message

**Solutions:**
1. **Check Server:** Is API server running? `curl http://localhost:8002/health`
2. **Check Port:** Default is 8002, verify correct port
3. **Firewall:** Ensure port 8002 is accessible
4. **Restart:** Stop and restart API server

### **Wrong Results**

**Problem:** Results don't match expectations

**Solutions:**
1. **Check Expansions:** Toggle expansion display to see search terms
2. **Verify Filters:** Review active filters (badge shows count)
3. **Match Threshold:** Increase similarity threshold (slider)
4. **Report Issue:** Help us improve - report unexpected results

---

## **📚 Additional Resources**

**Training Materials:**
- Video tutorials: Coming soon
- Webinars: Monthly product demos
- Case studies: Success stories from users

**Support:**
- Documentation: `docs/` directory
- GitHub Issues: Bug reports and feature requests
- Email: team@tenderintel.org
- Community: GitHub Discussions

---

## **🎓 Learning Path**

### **Week 1: Basic Search**
- Day 1-2: Learn intelligent search and keyword expansion
- Day 3-4: Practice with common keywords (cloud, api, security)
- Day 5: Explore saved searches and history

### **Week 2: Advanced Features**
- Day 1-2: Master advanced filtering (all 8 categories)
- Day 3-4: Understand competitive intelligence dashboards
- Day 5: Practice data export and reporting

### **Week 3: Market Intelligence**
- Day 1-2: Interpret Service×Firm heatmap
- Day 3-4: Analyze firm scorecards and market metrics
- Day 5: Build comprehensive market analysis reports

---

## **🎯 Quick Reference**

**Most Used Features:**
- **Simple Search:** Type keyword → Press Enter
- **View Expansions:** Click lightning icon
- **Apply Filters:** Open filters panel → Select → Apply
- **Export Results:** Select items → Click Export
- **Save Search:** After search → Click Save Search

**Keyboard Shortcuts:**
- `Enter` - Execute search
- `Ctrl+K` (Cmd+K) - Focus search box
- `Esc` - Close modals/panels

**Common Searches:**
- Networking: `lan`, `wan`, `vpn`, `firewall`
- Cloud: `cloud`, `api`, `aws`, `azure`
- Security: `security`, `iam`, `siem`, `waf`
- Procurement: `rfp`, `tender`, `gem`, `cppp`

---

**🚀 Ready to find your next opportunity? Start searching at http://localhost:8080**
