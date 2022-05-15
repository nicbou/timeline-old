export function hasGeolocation(entry) {
  return (
    entry.extra_attributes.location
    && entry.extra_attributes.location.latitude
    && entry.extra_attributes.location.longitude
  );
}