# Venue Endpoints & Services - Documentation

## 🟢 ACTIVE FILES (Use these)

### Routes
**File**: `app/api/v1/venues/routes.py`

**Endpoints**:
- `GET /api/v1/venues/map` - Lightweight venue data for map markers
- `GET /api/v1/venues/list` - Venue data for list screens  
- `GET /api/v1/venues/{venue_id}` - Full venue details

**Response Schemas**: Defined in `app/api/v1/venues/schemas.py`

### Service
**File**: `app/api/v1/venues/service.py`

**Functions**:
- `get_venues_map_preview()` - Returns venues for map view
- `get_venues_list_view()` - Returns venues for list view
- `get_venue_by_id()` - Returns full venue details
  - **Important**: Calculates `favorites_count` dynamically from `user_favorite_venues` table
  - Reads `rating_average` and `review_count` directly from DB (should be kept updated)

### Schemas
**File**: `app/api/v1/venues/schemas.py`

**Classes**:
- `VenueBase` - Common fields for all venue views
- `VenueMapPreviewResponse` - Lightweight schema for map
- `VenueListResponse` - Schema for list view
- `VenueDetailResponse` - Full schema for detail view

**Important**: The `model_validator` in `VenueBase` must include all fields that need to be serialized. If a field is missing from the attribute list (lines 53-86), it will use the default value instead of the database value.

---

## 🔴 DEPRECATED FILES (Do not use)

### Legacy Routes
**File**: `app/api/v1/endpoints/venues.py`
- Marked as deprecated in OpenAPI docs
- Kept for backward compatibility only
- **Do not modify**

### Legacy Service  
**File**: `app/services/venues_service.py`
- Marked as deprecated with clear warnings
- **Do not modify**

---

## 📝 Statistics Fields

### favorites_count
- **Calculated**: Dynamically in `get_venue_by_id()` from `user_favorite_venues` table
- **Why**: Real-time accuracy for user interactions
- **Schema requirement**: Must be in `model_validator` attribute list

### rating_average & review_count
- **Stored**: Directly in `venues` table
- **Updated**: Should be updated by triggers or batch processes when reviews change
- **Why**: Performance - avoid expensive aggregations on every request

---

## 🔧 How to Add New Venue Fields

1. Add column to `Venue` model in `app/models/venues.py`
2. Add field to appropriate schema in `app/api/v1/venues/schemas.py`
3. **CRITICAL**: Add field name to `model_validator` attribute list (lines 53-86) in `VenueBase`
4. If field needs dynamic calculation, add logic to `get_venue_by_id()` in service

---

## ⚠️ Common Pitfalls

1. **Field returns default value instead of DB value**
   - Check if field is in `model_validator` attribute list
   - The validator only copies fields explicitly listed

2. **Endpoint not executing**
   - Make sure you're using routes from `app/api/v1/venues/routes.py`
   - Legacy endpoints in `app/api/v1/endpoints/venues.py` are deprecated

3. **Statistics showing 0**
   - Check `favorites_count` is calculated in `get_venue_by_id()`
   - Check `rating_average`/`review_count` are updated in DB
   - Verify field is in schema's `model_validator` attribute list
