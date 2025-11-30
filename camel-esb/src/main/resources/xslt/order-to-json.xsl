<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="text" encoding="UTF-8"/>
  <xsl:template match="/order">
    {
      "id": "<xsl:value-of select="id"/>",
      "customer": {
        "name": "<xsl:value-of select="customer/name"/>",
        "email": "<xsl:value-of select="customer/email"/>"
      },
      "items": [
        <xsl:for-each select="items/item">
          {"sku":"<xsl:value-of select="sku"/>", "qty":<xsl:value-of select="qty"/>}
          <xsl:if test="position() != last()">,</xsl:if>
        </xsl:for-each>
      ]
    }
  </xsl:template>
</xsl:stylesheet>
