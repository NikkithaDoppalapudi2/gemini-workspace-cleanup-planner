def build_prompt(users_df, base_prompt):
    table = users_df.to_string(index=False)
    return f"{base_prompt}\n\nUser Data:\n{table}"